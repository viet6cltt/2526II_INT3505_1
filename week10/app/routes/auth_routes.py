from flask import Blueprint, current_app, request, jsonify, g, make_response
from functools import wraps
import logging
import jwt
import pybreaker
from app.extensions import db, limiter
from app.models import AuditLog, User, UserRole
from app.utils.auth_utils import create_access_token, create_refresh_token, decode_token, revoke_token
from app.utils.notification_client import send_welcome_notification
from app.utils.token_revocation import (
    is_token_revoked,
    token_revocation_breaker,
    token_revocation_breaker_status,
)

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("app.audit")


def write_audit_log(action, status, user_id=None, details=None):
    log_extra = {
        "event_type": "audit",
        "action": action,
        "status": status,
        "user_id": user_id,
        "details": details or {},
        "ip_address": request.headers.get('X-Forwarded-For', request.remote_addr),
        "user_agent": request.headers.get('User-Agent', '')[:255],
    }

    if status == "success":
        audit_logger.info("audit event", extra=log_extra)
    else:
        audit_logger.warning("audit event", extra=log_extra)

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        status=status,
        ip_address=log_extra["ip_address"],
        user_agent=log_extra["user_agent"],
    )
    audit_log.set_details(details)

    try:
        db.session.add(audit_log)
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception(
            "failed to persist audit log",
            extra={"action": action, "status": status, "user_id": user_id},
        )

def _extract_bearer_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return None, ("Missing Authorization header", 401)
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0] != 'Bearer':
        return None, ("Invalid Authorization header format. Expected 'Bearer <token>'", 401)

    return parts[1], None

def jwt_required(token_type="access"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if token_type == "access":
                token, error = _extract_bearer_token()
                if error:
                    return jsonify({"error": error[0]}), error[1]
            else:
                token = request.cookies.get("refresh_token")
                if not token:
                    return jsonify({"error": "Missing refresh token"}), 401
            
            # Decode and validate the token
            try:
                payload = decode_token(token)
            except jwt.ExpiredSignatureError:
                logger.info("expired token rejected", extra={"token_type": token_type})
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidIssuerError:
                logger.warning("token with invalid issuer rejected", extra={"token_type": token_type})
                return jsonify({"error": "Invalid token issuer"}), 401
            except jwt.InvalidAudienceError:
                logger.warning("token with invalid audience rejected", extra={"token_type": token_type})
                return jsonify({"error": "Invalid token audience"}), 401
            except jwt.InvalidTokenError:
                logger.warning("invalid token rejected", extra={"token_type": token_type})
                return jsonify({"error": "Invalid token"}), 401
            
            if payload.get("type") != token_type:
                logger.warning(
                    "token with invalid type rejected",
                    extra={
                        "expected_token_type": token_type,
                        "actual_token_type": payload.get("type"),
                        "user_id": payload.get("sub"),
                    },
                )
                return jsonify({"error": f"Invalid token type. Expected '{token_type}'"}), 401
            
            user = User.query.get(payload.get("sub"))
            if not user:
                logger.warning(
                    "token references missing user",
                    extra={"token_type": token_type, "user_id": payload.get("sub")},
                )
                return jsonify({"error": "User not found"}), 404
            
            # handle token revocation
            try:
                revoked_token = is_token_revoked(payload["jti"])
            except pybreaker.CircuitBreakerError:
                logger.error(
                    "token revocation circuit breaker is open",
                    extra={"user_id": user.id, "token_type": token_type},
                )
                return jsonify({
                    "error": "Token revocation service is temporarily unavailable",
                    "circuit_breaker": token_revocation_breaker_status(),
                }), 503
            except Exception:
                logger.exception(
                    "token revocation check failed",
                    extra={"user_id": user.id, "token_type": token_type},
                )
                return jsonify({
                    "error": "Token revocation service failed",
                    "circuit_breaker": token_revocation_breaker_status(),
                }), 503

            if revoked_token:
                logger.warning(
                    "revoked token rejected",
                    extra={"user_id": user.id, "token_type": token_type},
                )
                return jsonify({"error": "Token has been revoked"}), 401
            
            g.current_user = user
            g.payload = payload

            return f(*args, **kwargs)
        return wrapper
    return decorator
        
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = getattr(g, "current_user", None)
            payload = getattr(g, "payload", None)
            
            if not payload or not user:
                return jsonify({"error": "Unauthorized. Please log in to access this resource"}), 401
            
            token_role = payload.get("role")
            if token_role != required_role:
                return jsonify({"error": "Forbidden. You have no right to access this resource"}), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

auth_bp = Blueprint('api/v1/auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute") 
def login():
    data = request.get_json() or {}
    
    username = data.get('username', "")
    password = data.get('password', "")
    
    if not username or not password:
        logger.warning(
            "login rejected because credentials are missing",
            extra={"username": username},
        )
        write_audit_log(
            "auth.login",
            "failure",
            details={"reason": "missing_credentials", "username": username}
        )
        return jsonify({"error": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        logger.warning(
            "login rejected because credentials are invalid",
            extra={"username": username, "user_id": user.id if user else None},
        )
        write_audit_log(
            "auth.login",
            "failure",
            user_id=user.id if user else None,
            details={"reason": "invalid_credentials", "username": username}
        )
        return jsonify({"error": "Invalid username or password"}), 401
    
    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)
    logger.info(
        "user logged in",
        extra={"user_id": user.id, "username": user.username, "role": user.role.value},
    )
    write_audit_log(
        "auth.login",
        "success",
        user_id=user.id,
        details={"username": user.username, "role": user.role.value}
    )
    
    response = make_response(jsonify({
        "message": "Login successfully",
        "data": {
            "access_token": access_token,
            "user": user.to_dict()
        }
    }))
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True, # Không cho phép truy cập token từ JavaScript
        secure=True, # Chỉ gửi cookie qua HTTPS
        samesite="None", # For demo app
        max_age=current_app.config["REFRESH_TOKEN_EXPIRES_IN"]
    )
    
    return response, 200

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("100 per hour")
def register():
    data = request.get_json() or {}
    
    username = data.get('username', "")
    password = data.get('password', "")
    email = data.get('email', "")
    
    if not username or not password:
        logger.warning(
            "registration rejected because credentials are missing",
            extra={"username": username, "email": email},
        )
        write_audit_log(
            "auth.register",
            "failure",
            details={"reason": "missing_credentials", "username": username, "email": email}
        )
        return jsonify({"error": "Username and password are required"}), 400
    
    if User.query.filter_by(username=username).first():
        logger.warning(
            "registration rejected because username already exists",
            extra={"username": username, "email": email},
        )
        write_audit_log(
            "auth.register",
            "failure",
            details={"reason": "username_exists", "username": username, "email": email}
        )
        return jsonify({"error": "Username already exists"}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    
    if email == "vietphan@gmail.com":
        user.role = UserRole.ADMIN  
        
    db.session.add(user)
    db.session.commit()
    logger.info(
        "user registered",
        extra={"user_id": user.id, "username": user.username, "role": user.role.value},
    )
    write_audit_log(
        "auth.register",
        "success",
        user_id=user.id,
        details={"username": user.username, "email": user.email, "role": user.role.value}
    )
    try:
        result = send_welcome_notification(user)
        if result.get("status") == "fallback":
            write_audit_log(
                "notification.welcome",
                "failure",
                user_id=user.id,
                details={
                    "reason": "fallback",
                    "username": user.username,
                    "email": user.email,
                }
            )
        else:
            write_audit_log(
                "notification.welcome",
                "success",
                user_id=user.id,
                details={
                    "username": user.username,
                    "email": user.email,
                }
            )
    except Exception as exc:
        logger.exception(
            "welcome notification failed",
            extra={"user_id": user.id, "username": user.username},
        )
        write_audit_log(
            "notification.welcome",
            "failure",
            user_id=user.id,
            details={"error": str(exc)}
        )
    
    return jsonify({
        "message": "User registered successfully",
        "data": user.to_dict()
    }), 201
    
@auth_bp.route('/register-admin', methods=['POST'])
@jwt_required(token_type="access")
@role_required("admin")
def admin_register():
    data = request.get_json() or {}
    
    username = data.get('username', "")
    password = data.get('password', "")
    email = data.get('email', "")
    
    if not username or not password:
        logger.warning(
            "admin registration rejected because credentials are missing",
            extra={"actor_user_id": g.current_user.id, "username": username, "email": email},
        )
        write_audit_log(
            "auth.register_admin",
            "failure",
            user_id=g.current_user.id,
            details={"reason": "missing_credentials", "username": username, "email": email}
        )
        return jsonify({"error": "Username and password are required"}), 400
    
    if User.query.filter_by(username=username).first():
        logger.warning(
            "admin registration rejected because username already exists",
            extra={"actor_user_id": g.current_user.id, "username": username, "email": email},
        )
        write_audit_log(
            "auth.register_admin",
            "failure",
            user_id=g.current_user.id,
            details={"reason": "username_exists", "username": username, "email": email}
        )
        return jsonify({"error": "Username already exists"}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    
    user.role = UserRole.ADMIN
        
    db.session.add(user)
    db.session.commit()
    logger.info(
        "admin user registered",
        extra={
            "actor_user_id": g.current_user.id,
            "created_user_id": user.id,
            "created_username": user.username,
        },
    )
    write_audit_log(
        "auth.register_admin",
        "success",
        user_id=g.current_user.id,
        details={
            "created_user_id": user.id,
            "created_username": user.username,
            "created_email": user.email,
        }
    )
    
    return jsonify({
        "message": "User registered successfully",
        "data": user.to_dict()
    }), 201

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(token_type="refresh")
def refresh():
    user = g.current_user
    
    access_token = create_access_token(user.id, user.role.value)
    logger.info("access token refreshed", extra={"user_id": user.id})
    write_audit_log(
        "auth.refresh",
        "success",
        user_id=user.id,
        details={"username": user.username}
    )
    
    return jsonify({
        "message": "Token refreshed successfully",
        "data": {
            "access_token": access_token
        }
    }), 200
    
@auth_bp.route('/logout', methods=['POST'])
@jwt_required(token_type="access")
def logout():
    # Revoke access token
    payload = g.payload
    revoke_token(payload)
    
    # Revoke refresh token
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        try:
            refresh_payload = decode_token(refresh_token)
            revoke_token(refresh_payload)
        except jwt.InvalidTokenError:
            logger.warning(
                "invalid refresh token ignored during logout",
                extra={"user_id": g.current_user.id},
            )
            pass # Ignore invalid token
        
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie("refresh_token", "", expires=0, httponly=True, secure=True, samesite="None")
    logger.info("user logged out", extra={"user_id": g.current_user.id})
    write_audit_log(
        "auth.logout",
        "success",
        user_id=g.current_user.id,
        details={"username": g.current_user.username}
    )
    
    return response, 200

@auth_bp.route('/test', methods=['GET'])
@jwt_required(token_type="access")
def test():
    return jsonify({
        "message": "Test endpoint is working",
        "user": g.current_user.to_dict()
    }), 200

@auth_bp.route('/audit-logs', methods=['GET'])
@jwt_required(token_type="access")
@role_required("admin")
def get_audit_logs():
    limit = request.args.get("limit", default=50, type=int)
    limit = min(max(limit, 1), 200)

    logs = (
        AuditLog.query
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )

    logger.info("audit logs retrieved", extra={"limit": limit, "user_id": g.current_user.id})

    return jsonify({
        "message": "Audit logs retrieved successfully",
        "data": [log.to_dict() for log in logs]
    }), 200

@auth_bp.route('/circuit-breaker/token-revocation', methods=['GET'])
@limiter.exempt
def get_token_revocation_circuit_breaker():
    return jsonify({
        "message": "Token revocation circuit breaker status",
        "data": token_revocation_breaker_status()
    }), 200

@auth_bp.route('/circuit-breaker/token-revocation/reset', methods=['POST'])
@limiter.exempt
def reset_token_revocation_circuit_breaker():
    token_revocation_breaker.close()

    return jsonify({
        "message": "Token revocation circuit breaker reset",
        "data": token_revocation_breaker_status()
    }), 200
    
    
    

    



        
        
