import os 
import secrets
from urllib.parse import urlencode

from dotenv import load_dotenv
from flask import Flask, request, jsonify, redirect, session, redirect
from flask_cors import CORS
import requests
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("CLIENT_SESSION_SECRET") # dùng để mã hóa session cookie
CORS(app, supports_credentials=True, origin=["http://localhost:5173"]) 

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # Cho phép gửi cookie khi redirect quay lại
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_NAME='client_session'
)

# for frontend
FRONTEND_URI = "http://localhost:5173"
# for auth_server 
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_SERVER_URI = os.getenv("AUTH_SERVER_URI")
REDIRECT_URI = os.getenv("REDIRECT_URI")
#for google server 
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_AUTH_URI = os.getenv("GOOGLE_AUTH_URI")
GOOGLE_TOKEN_URI = os.getenv("GOOGLE_TOKEN_URI")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


# bên phía client
# cho auth_server
@app.route('/login', methods=['GET'])
def login():
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state

    
    query = urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "profile",
        "state": state
    })
    
    print(f"Redirecting to: {AUTH_SERVER_URI}/authorize?{query}")

    return redirect(f"{AUTH_SERVER_URI}/authorize?{query}")

# cho google server 
@app.route('/login-google', methods=['GET'])
def login_google():
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state

    query = urlencode({
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "state": state,
        "access_type": "online", # only access token, không có refresh token 
        "prompt": "select_account" # hiện bảng chọn tài khoản
    })

    print(f"Redirecting to: {GOOGLE_AUTH_URI}?{query}")

    return redirect(f"{GOOGLE_AUTH_URI}?{query}")

# bên phía client
@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    saved_state = session.pop('oauth_state', None)
    
    if not code:
        return jsonify({"error": "Authorization code is missing"}), 400
    
    if not state or state != saved_state:
        return jsonify({"error": "Invalid state"}), 400
    
    token_response = requests.post(f"{AUTH_SERVER_URI}/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }, timeout=10
    )
    
    if token_response.status_code != 200:
        return jsonify({"error": "Failed to exchange authorization code for token"}), 400
    
    token_data = token_response.json()
    session["access_token"] = token_data["data"]["access_token"]
    session["oauth_provider"] = "auth_server"
    
    # Có thể tạo thêm access token riêng cho client backend nếu muốn 
    return redirect(f"{FRONTEND_URI}/success")

# callback cho google server
@app.route('/callback-google', methods=['GET'])
def callback_google():
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    saved_state = session.pop('oauth_state', None)
    
    # Check for errors
    if error:
        return jsonify({"error": f"Google authorization failed: {error}"}), 400
    
    if not code or state != saved_state: 
        return jsonify({"error": "Invalid state or missing authorization code"}), 400
    
    token_response = requests.post(GOOGLE_TOKEN_URI, data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI
    }, timeout=10
    )    
    
    if token_response.status_code != 200:
        return jsonify({"error": "Failed to exchange authorization code for token"}), 400
    
    token_data = token_response.json()
    session["access_token"] = token_data.get("access_token")
    session["oauth_provider"] = "google"
    
    return redirect(f"{FRONTEND_URI}/success")

# bên phía client
@app.route("/session", methods=['GET'])
def get_session():
    # lấy access token từ cookies được gửi lên (client_session)
    access_token = session.get("access_token")
    provider = session.get("oauth_provider")
    
    if not access_token:
        return jsonify({"error": "No active session"}), 401
    
    if provider == "auth_server":
        response = requests.get(f"{AUTH_SERVER_URI}/profile", 
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
    elif provider == "google":
        response = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", 
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch user profile"}), response.status_code
    
    return jsonify({
        "message": "User profile fetched successfully",
        "data": response.json(),
        "metadata": {
            "oauth_provider": provider
        }
    })
  
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(f"{AUTH_SERVER_URI}/logout")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
    
    
    
    

