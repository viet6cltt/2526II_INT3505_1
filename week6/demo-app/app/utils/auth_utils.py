import uuid
from datetime import datetime, timedelta, timezone
import jwt
from flask import current_app
from app.extensions import db, redis_client
from app.models import User

def utc_now():
    return datetime.now(timezone.utc)

def create_access_token(user_id, user_role, expires_in=current_app.config["ACCESS_TOKEN_EXPIRES_IN"]):
    now = utc_now()
    exp = now + timedelta(seconds=expires_in)
    
    payload = {
        "sub": str(user_id), # Định danh người dùng
        "role": user_role,
        "type": "access", # Loại token
        "jti": str(uuid.uuid4().hex), # Unique ID cho token
        "iat": now.timestamp(), # Thời điểm tạo token
        "nbf": now.timestamp(), # Thời điểm token có hiệu lực
        "exp": exp.timestamp(), # Thời điểm token hết hạn
        "iss": "demo-app", # Nhà phát hành token
        "aud": "demo-app-users" # Đối tượng sử dụng token
    }
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def create_refresh_token(user_id, expires_in=current_app.config["REFRESH_TOKEN_EXPIRES_IN"]):
    now = utc_now()
    exp = now + timedelta(seconds=expires_in)
    
    payload = {
        "sub": str(user_id), # Định danh người dùng
        "type": "refresh", # Loại token
        "jti": str(uuid.uuid4().hex), # Unique ID cho token
        "iat": now.timestamp(), # Thời điểm tạo token
        "nbf": now.timestamp(), # Thời điểm token có hiệu lực
        "exp": exp.timestamp(), # Thời điểm token hết hạn
        "iss": "demo-app", # Nhà phát hành token
        "aud": "demo-app-users" # Đối tượng sử dụng token
    }
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def decode_token(token):
    payload = jwt.decode(token, 
        current_app.config['SECRET_KEY'],
        algorithms=['HS256'],
        audience='demo-app-users',
        issuer='demo-app',
        options={
            'require': ['sub', 'exp', 'iat', 'nbf', 'jti']
        })
    return payload

def revoke_token(payload):
    jti = payload['jti']
    exp = payload['exp']
    
    # Lưu vào redis với thời gian tồn tại = thời gian còn lại của refresh token
    redis_client.setex(f"revoked_token:{jti}", exp - int(utc_now().timestamp()), "true")

    