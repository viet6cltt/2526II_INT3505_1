import requests
from flask import current_app


def send_welcome_notification(user):
    base_url = current_app.config["NOTIFICATION_SERVICE_URL"].rstrip("/")
    payload = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }

    response = requests.post(
        f"{base_url}/notify/welcome",
        json=payload,
        timeout=2,
    )
    response.raise_for_status()
    return response.json()
