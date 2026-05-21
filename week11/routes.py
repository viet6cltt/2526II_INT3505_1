import json
import os
from datetime import datetime, UTC

from flask import Blueprint, jsonify, request, url_for


notifications_bp = Blueprint("notifications", __name__)

# Data is reset whenever the Flask app restarts.
notifications = {}
next_id = 1
EVENT_LOG_FILE = os.path.join(os.path.dirname(__file__), "event_logs.jsonl")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "notification_events")


def error_response(message, status_code):
    return jsonify({
        "success": False,
        "message": message,
    }), status_code


def get_notification(notification_id):
    notification = notifications.get(notification_id)
    if notification is None:
        return None, error_response("Notification not found", 404)
    return notification, None


def parse_positive_int(value, field_name):
    try:
        parsed_value = int(value)
    except (TypeError, ValueError):
        return None, error_response(f"Query param '{field_name}' must be an integer", 400)

    if parsed_value < 1:
        return None, error_response(f"Query param '{field_name}' must be greater than 0", 400)

    return parsed_value, None


def append_event_log(event_name, payload, source, publish_status):
    log_entry = {
        "event_name": event_name,
        "payload": payload,
        "source": source,
        "publish_status": publish_status,
        "created_at": datetime.now(UTC).isoformat(),
    }
    with open(EVENT_LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")
    return log_entry


def read_event_logs():
    if not os.path.exists(EVENT_LOG_FILE):
        return []

    logs = []
    with open(EVENT_LOG_FILE, "r", encoding="utf-8") as log_file:
        for line in log_file:
            line = line.strip()
            if line:
                logs.append(json.loads(line))
    return logs


def publish_event(event_name, payload):
    print(
        f"[publisher] publishing {event_name} to {RABBITMQ_HOST}/{RABBITMQ_QUEUE}: {payload}",
        flush=True,
    )
    try:
        import pika
    except ImportError:
        append_event_log(event_name, payload, "publisher", "pika_not_installed")
        print("[publisher] publish skipped: pika is not installed", flush=True)
        return False

    connection = None
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=False)
        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps({
                "event_name": event_name,
                "payload": payload,
            }),
        )
        append_event_log(event_name, payload, "publisher", "published")
        print(f"[publisher] published {event_name}", flush=True)
        return True
    except Exception as exc:
        append_event_log(event_name, payload, "publisher", "publish_failed")
        print(f"[publisher] publish failed: {exc}", flush=True)
        return False
    finally:
        if connection is not None and connection.is_open:
            connection.close()


def notification_response_data(notification):
    return {
        **notification,
        "_links": {
            "self": {
                "href": url_for("notifications.get_notification_detail", notification_id=notification["id"])
            },
            "update": {
                "href": url_for("notifications.update_notification", notification_id=notification["id"])
            },
            "delete": {
                "href": url_for("notifications.delete_notification", notification_id=notification["id"])
            },
            "mark_read": {
                "href": url_for("notifications.mark_notification_as_read", notification_id=notification["id"])
            },
        },
    }


@notifications_bp.post("/notifications")
def create_notification():
    global next_id

    data = request.get_json(silent=True) or {}
    message = data.get("message")
    status = data.get("status", "unread")
    notification_type = data.get("type", "general")
    user_id = data.get("user_id")

    if not isinstance(message, str) or not message.strip():
        return error_response("Field 'message' is required", 400)
    if not isinstance(status, str) or not status.strip():
        return error_response("Field 'status' must be a non-empty string", 400)
    if not isinstance(notification_type, str) or not notification_type.strip():
        return error_response("Field 'type' must be a non-empty string", 400)
    if user_id is not None:
        user_id, error = parse_positive_int(user_id, "user_id")
        if error:
            return error

    notification = {
        "id": next_id,
        "message": message.strip(),
        "status": status.strip(),
        "type": notification_type.strip(),
        "user_id": user_id,
    }
    notifications[next_id] = notification
    next_id += 1
    publish_event("notification.created", notification)

    return jsonify({
        "success": True,
        "message": "Notification created",
        "data": notification_response_data(notification),
    }), 201


@notifications_bp.get("/notifications")
def list_notifications():
    status = request.args.get("status")
    notification_type = request.args.get("type")
    user_id = request.args.get("user_id")
    page = request.args.get("page", 1)
    limit = request.args.get("limit", 10)

    page, error = parse_positive_int(page, "page")
    if error:
        return error

    limit, error = parse_positive_int(limit, "limit")
    if error:
        return error

    if user_id is not None:
        user_id, error = parse_positive_int(user_id, "user_id")
        if error:
            return error

    filtered_notifications = list(notifications.values())

    if status:
        filtered_notifications = [
            notification
            for notification in filtered_notifications
            if notification["status"] == status
        ]

    if notification_type:
        filtered_notifications = [
            notification
            for notification in filtered_notifications
            if notification["type"] == notification_type
        ]

    if user_id is not None:
        filtered_notifications = [
            notification
            for notification in filtered_notifications
            if notification["user_id"] == user_id
        ]

    total = len(filtered_notifications)
    start = (page - 1) * limit
    end = start + limit
    paginated_notifications = filtered_notifications[start:end]

    return jsonify({
        "success": True,
        "message": "Notifications retrieved",
        "data": [notification_response_data(notification) for notification in paginated_notifications],
        "page": page,
        "limit": limit,
        "total": total,
    }), 200


@notifications_bp.get("/events")
def list_event_logs():
    return jsonify({
        "success": True,
        "message": "Event logs retrieved",
        "data": read_event_logs(),
    }), 200


@notifications_bp.get("/notifications/<int:notification_id>")
def get_notification_detail(notification_id):
    notification, error = get_notification(notification_id)
    if error:
        return error

    return jsonify({
        "success": True,
        "message": "Notification retrieved",
        "data": notification_response_data(notification),
    }), 200


@notifications_bp.patch("/notifications/<int:notification_id>")
def update_notification(notification_id):
    notification, error = get_notification(notification_id)
    if error:
        return error

    data = request.get_json(silent=True) or {}
    allowed_fields = {"message", "status"}
    update_fields = allowed_fields.intersection(data)

    if not update_fields:
        return error_response("Provide 'message' or 'status' to update", 400)

    for field in update_fields:
        value = data[field]
        if not isinstance(value, str) or not value.strip():
            return error_response(f"Field '{field}' must be a non-empty string", 400)
        notification[field] = value.strip()

    return jsonify({
        "success": True,
        "message": "Notification updated",
        "data": notification_response_data(notification),
    }), 200


@notifications_bp.patch("/notifications/<int:notification_id>/read")
def mark_notification_as_read(notification_id):
    notification, error = get_notification(notification_id)
    if error:
        return error

    notification["status"] = "read"

    return jsonify({
        "success": True,
        "message": "Notification marked as read",
        "data": notification_response_data(notification),
    }), 200


@notifications_bp.delete("/notifications/<int:notification_id>")
def delete_notification(notification_id):
    notification, error = get_notification(notification_id)
    if error:
        return error

    del notifications[notification_id]
    return jsonify({
        "success": True,
        "message": "Notification deleted",
        "data": notification_response_data(notification),
    }), 200
