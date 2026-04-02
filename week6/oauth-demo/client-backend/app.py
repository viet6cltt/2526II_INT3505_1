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

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTH_SERVER_URI = os.getenv("AUTH_SERVER_URI")
REDIRECT_URI = os.getenv("REDIRECT_URI")
FRONTEND_URI = "http://localhost:5173"


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

@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    saved_state = session.pop('oauth_state', None)
    print(f"All Cookies: {request.cookies}")
    print(state, saved_state)
    
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
    
    # Có thể tạo thêm access token riêng cho client backend nếu muốn 
    return redirect(f"{FRONTEND_URI}/success")

@app.route("/session", methods=['GET'])
def get_session():
    access_token = session.get("access_token")
    if not access_token:
        return jsonify({"error": "No active session"}), 401
    
    response = requests.get(f"{AUTH_SERVER_URI}/profile", 
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10
    )
    return jsonify({
        "message": "Get session successfully",
        "data": response.json()
    }), 200
    
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(f"{AUTH_SERVER_URI}/logout")

if __name__ == '__main__':
    app.run(port=5001, debug=True)
    
    
    
    
    

