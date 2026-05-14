import logging

import requests
from flask import current_app
import pybreaker 


logger = logging.getLogger(__name__)

notificaton_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=15,
    name="notification_service",
)

def notificaton_breaker_status():
    return {
        "name": notificaton_breaker.name,
        "state": notificaton_breaker.current_state,
        "failure_count": notificaton_breaker.fail_counter,
        "failure_threshold": notificaton_breaker.fail_max,
        "recovery_timeout": notificaton_breaker.reset_timeout,
    }
    
def fallback_welcome_notification(user, reason):
    logger.warning(
        "welcome notification fallback",
        extra={
            "user_id": user.id,
            "username": user.username,
            "reason": reason,
            "breaker_state": notificaton_breaker.current_state,
        },
    )
    
    return {
        "status": "fallback",
        "message": "Failed to send welcome notification, using fallback method.",
        "user_id": user.id,
    }

@notificaton_breaker
def _send_welcome_notification(user):
    base_url = current_app.config["NOTIFICATION_SERVICE_URL"].rstrip("/")
    payload = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }

    logger.info(
        "sending welcome notification",
        extra={"user_id": user.id, "username": user.username, "notification_url": base_url},
    )
    response = requests.post(
        f"{base_url}/notify/welcome",
        json=payload,
        timeout=2,
    )
    response.raise_for_status()
    logger.info(
        "welcome notification sent",
        extra={"user_id": user.id, "status_code": response.status_code},
    )
    return response.json()
    
    

def send_welcome_notification(user):
    try:
        return _send_welcome_notification(user)

    except pybreaker.CircuitBreakerError:
        return fallback_welcome_notification(user, "circuit_breaker_open")

    except requests.RequestException as exc:
        return fallback_welcome_notification(user, str(exc))
