from flask import Blueprint, jsonify, request


notifications_bp = Blueprint("notifications", __name__)

# Data is reset whenever the Flask app restarts.
notifications = {}
next_id = 1


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

    return jsonify({
        "success": True,
        "message": "Notification created",
        "data": notification,
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
        "data": paginated_notifications,
        "page": page,
        "limit": limit,
        "total": total,
    }), 200


@notifications_bp.get("/notifications/<int:notification_id>")
def get_notification_detail(notification_id):
    notification, error = get_notification(notification_id)
    if error:
        return error

    return jsonify({
        "success": True,
        "message": "Notification retrieved",
        "data": notification,
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
        "data": notification,
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
        "data": notification,
    }), 200
