import os 
import time
import secrets
from urllib.parse import urlencode

import jwt
from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, session, make_response
from flask_cors import CORS 
from datetime import datetime, timedelta, timezone

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("AUTH_SERVER_SECRET")
CORS(app, supports_credentials=True) # cho phép gửi cookie từ client

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # Cho phép gửi cookie khi redirect quay lại
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_NAME='authorization_server_session'
)

JWT_SECRET = os.getenv("JWT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_REDIRECT_URI = os.getenv("CLIENT_REDIRECT_URI")

# demo DB 
USERS = {
    "viet@example.com": {
        "name": "Viet Phan",
        "password": "123"
    }
}

AUTH_CODES = {}
ACCESS_TOKENS = {}

def create_access_token(username):
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=3600)
    
    payload = {
        "sub": str(username),
        "type": "access",
        "iat": now.timestamp(),
        "nbf": now.timestamp(),
        "exp": exp.timestamp(),
        "iss": "auth-server",
        "aud": "client-app"
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    ACCESS_TOKENS[token] = username
    return token

def verify_access_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'], audience='client-app', issuer='auth-server')
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
@app.route('/authorize', methods=['GET'])
def authorize():
    response_type = request.args.get('response_type') # must be "code"
    client_id = request.args.get('client_id') # must match CLIENT_ID
    redirect_uri = request.args.get('redirect_uri') # must match CLIENT_REDIRECT_URI
    state = request.args.get('state') # optional, will be sent back to client
    scope = request.args.get('scope', 'profile')
    
    if response_type != 'code':
        return jsonify({"error": "Unsupported response type"}), 400
    if client_id != CLIENT_ID:
        return jsonify({"error": "Invalid client_id"}), 400
    if redirect_uri != CLIENT_REDIRECT_URI:
        return jsonify({"error": "Invalid redirect_uri"}), 400
    
    # Nếu chưa đăng nhập, hiển thị form đăng nhập
    if 'username' not in session:
        return '''
            <form method="post" action="/login">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="state" value="{state}">
                <input type="hidden" name="scope" value="{scope}">
                <label>Email: <input type="email" name="username"></label><br>
                <label>Password: <input type="password" name="password"></label><br>
                <button type="submit">Login</button>
            </form>
        '''.format(client_id=client_id, redirect_uri=redirect_uri, state=state, scope=scope) 
        
    username = session['username']
    code = secrets.token_urlsafe(16)
    AUTH_CODES[code] = {
        "username": username,
        "client_id": client_id,
        "scope": scope,
        "expires_at": time.time() + 600, # code có hiệu lực 10 phút
        "used": False,
        "redirect_uri": redirect_uri
    }
    
    print(f"code: {code}, AUTH_CODES: {AUTH_CODES.get(code)}")
    
    params = {"code": code }
    if state:
        params["state"] = state
        
    return redirect(f"{redirect_uri}?{urlencode(params)}")
    
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    client_id = request.form.get('client_id')
    redirect_uri = request.form.get('redirect_uri')
    state = request.form.get('state')
    scope = request.form.get('scope')
    
    user = USERS.get(username)
    if not user or user['password'] != password:
        return "<h3>Invalid credentials</h3>", 401
    
    session['username'] = username # đánh dấu user đã đăng nhập
    
    
    
    query = urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": scope
    })

    return redirect(f"/authorize?{query}")

@app.route('/token', methods=['POST'])
def token():
    grant_type = request.form.get('grant_type') # must be "authorization_code"
    code = request.form.get('code')
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    redirect_uri = request.form.get('redirect_uri')
    
    if grant_type != 'authorization_code':
        print("Unsupported grant type")
        return jsonify({"error": "Unsupported grant type"}), 400
    if client_id != CLIENT_ID or client_secret != CLIENT_SECRET:
        print("Invalid client credentials")
        return jsonify({"error": "Invalid client credentials"}), 401
    
    auth_code = AUTH_CODES.get(code)
    if not auth_code:
        print("Invalid authorization code")
        return jsonify({"error": "Invalid authorization code"}), 400
    if auth_code['used']:
        print("Authorization code already used")
        return jsonify({"error": "Authorization code already used"}), 400
    if time.time() > auth_code['expires_at']:
        print("Authorization code expired")
        return jsonify({"error": "Authorization code expired"}), 400
    if auth_code['redirect_uri'] != redirect_uri:
        print("Invalid redirect_uri")
        return jsonify({"error": "Invalid redirect_uri"}), 400
    
    auth_code['used'] = True
    access_token = create_access_token(auth_code['username'])
    
    return jsonify({
        "message": "Token issued successfully",
        "data": {
            "access_token": access_token,
            "expires_in": 3600,
            "scope": auth_code['scope']
        }
    })
    
@app.route('/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401
    
    token = auth_header.split(' ')[1]
    username = verify_access_token(token) 
    if not username:
        return jsonify({"error": "Invalid or expired access token"}), 401
    
    user = USERS.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "username": username,
        "name": user['name']

    })   
    
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)


