from flask import Blueprint, current_app, request, jsonify, g, make_response
from functools import wraps
import jwt
from app.extensions import db, redis_client
from app.models import User
from app.utils.auth_utils import create_access_token, create_refresh_token, decode_token, revoke_token

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
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            except jwt.InvalidIssuerError:
                return jsonify({"error": "Invalid token issuer"}), 401
            except jwt.InvalidAudienceError:
                return jsonify({"error": "Invalid token audience"}), 401
            
            if payload.get("type") != token_type:
                return jsonify({"error": f"Invalid token type. Expected '{token_type}'"}), 401
            
            user = User.query.get(payload.get("sub"))
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # handle token revocation
            if redis_client.get(f"revoked_token:{payload['jti']}"):
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
                return jsonify({"error": "Unauthorized"}), 401
            
            token_role = payload.get("role")
            if token_role != required_role:
                return jsonify({"error": "Forbidden"}), 403
            
            return f(*args, **kwargs)
        return wrapper
    return decorator

auth_bp = Blueprint('api/v1/auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    
    username = data.get('username', "")
    password = data.get('password', "")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    
    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)
    
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
def register():
    data = request.get_json() or {}
    
    username = data.get('username', "")
    password = data.get('password', "")
    email = data.get('email', "")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "User registered successfully",
        "data": user.to_dict()
    }), 201
    
    
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(token_type="refresh")
def refresh():
    user = g.current_user
    
    access_token = create_access_token(user.id, user.role.value)
    
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
            pass # Ignore invalid token
        
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie("refresh_token", "", expires=0, httponly=True, secure=True, samesite="None")
    
    return response, 200
    
    
    

    



        
        