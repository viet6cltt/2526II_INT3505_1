from flask import Blueprint, request, jsonify, g
from functools import wraps
import jwt
from app.extensions import db
from app.models import User
from app.utils.auth_utils import create_access_token, decode_access_token

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
            token, error = _extract_bearer_token()
            if error:
                return jsonify({"error": error[0]}), error[1]
            
            try:
                payload = decode_access_token(token)
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token"}), 401
            except jwt.InvalidIssuerError:
                return jsonify({"error": "Invalid token issuer"}), 401
            except jwt.InvalidAudienceError:
                return jsonify({"error": "Invalid token audience"}), 401
            
            if payload.get("type") != "access":
                return jsonify({"error": "Invalid token type"}), 401
            
            user = User.query.get(payload.get("sub"))
            if not user:
                return jsonify({"error": "User not found"}), 404
            
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

auth_bp = Blueprint('auth', __name__)

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
    
    access_token = create_access_token(user.id, user.role)
    
    return jsonify({
        "data": {
            "access_token": access_token,
            "user": user.to_dict()
        }
    }), 200

    



        
        