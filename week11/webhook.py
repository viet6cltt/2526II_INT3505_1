import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

subscribers = {}
notifications = {}
deliveries = {}
received_webhooks = []


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def build_signature(secret, raw_body):
    return hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()


def json_body():
    return request.get_json(silent=True) or {}


def subscriber_links(subscriber_id):
    return {
        "self": f"/api/subscribers/{subscriber_id}",
        "deliveries": f"/api/deliveries?subscriber_id={subscriber_id}",
        "notifications": f"/api/notifications?subscriber_id={subscriber_id}",
    }


def notification_links(notification_id):
    return {
        "self": f"/api/notifications/{notification_id}",
        "deliveries": f"/api/deliveries?notification_id={notification_id}",
    }


def delivery_links(delivery_id):
    return {
        "self": f"/api/deliveries/{delivery_id}",
        "retry": f"/api/deliveries/{delivery_id}/retry",
    }


def paginate(items):
    try:
        page = max(int(request.args.get("page", 1)), 1)
        limit = max(int(request.args.get("limit", 20)), 1)
    except ValueError:
        page = 1
        limit = 20
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total": len(items),
        "items": items[start:end],
    }


def matches_filters(item, filters):
    for key, value in filters.items():
        if value is None:
            continue
        if str(item.get(key)) != value:
            return False
    return True


def send_webhook(subscriber, event_type, payload, notification_id, retry_of=None):
    delivery_id = new_id("dlv")
    raw_body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    signature = build_signature(subscriber["secret"], raw_body)
    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Event": event_type,
        "X-Webhook-Delivery": delivery_id,
        "X-Webhook-Subscriber": subscriber["id"],
        "X-Webhook-Signature": signature,
    }

    delivery = {
        "id": delivery_id,
        "notification_id": notification_id,
        "subscriber_id": subscriber["id"],
        "callback_url": subscriber["callback_url"],
        "event_type": event_type,
        "status": "pending",
        "attempted_at": utc_now(),
        "retry_of": retry_of,
        "response_code": None,
        "response_body": None,
        "links": delivery_links(delivery_id),
    }

    try:
        response = requests.post(
            subscriber["callback_url"],
            data=raw_body,
            headers=headers,
            timeout=3,
        )
        delivery["response_code"] = response.status_code
        delivery["response_body"] = response.text[:500]
        delivery["status"] = "delivered" if 200 <= response.status_code < 300 else "failed"
    except requests.RequestException as exc:
        delivery["status"] = "failed"
        delivery["response_body"] = str(exc)

    deliveries[delivery_id] = delivery
    return delivery


def create_notification(event_type, data):
    notification_id = new_id("ntf")
    notification = {
        "id": notification_id,
        "event_type": event_type,
        "status": "created",
        "data": data,
        "created_at": utc_now(),
        "links": notification_links(notification_id),
    }
    notifications[notification_id] = notification
    return notification


@app.get("/")
def index():
    return jsonify(
        {
            "message": "Week 13 API Design Patterns demo",
            "resources": {
                "subscribers": "/api/subscribers",
                "events": "/api/events",
                "notifications": "/api/notifications",
                "deliveries": "/api/deliveries",
                "demo_receiver": "/webhooks/demo-receiver",
            },
        }
    )


@app.post("/api/subscribers")
def create_subscriber():
    body = json_body()
    required_fields = ["name", "event_types", "callback_url", "secret"]
    missing = [field for field in required_fields if not body.get(field)]
    if missing:
        return jsonify({"error": "Missing required fields", "missing": missing}), 400

    subscriber_id = new_id("sub")
    subscriber = {
        "id": subscriber_id,
        "name": body["name"],
        "event_types": body["event_types"],
        "callback_url": body["callback_url"],
        "secret": body["secret"],
        "created_at": utc_now(),
        "links": subscriber_links(subscriber_id),
    }
    subscribers[subscriber_id] = subscriber
    return jsonify(subscriber), 201


@app.get("/api/subscribers")
def list_subscribers():
    event_type = request.args.get("event_type")
    name = request.args.get("name")

    items = [
        subscriber
        for subscriber in subscribers.values()
        if matches_filters(subscriber, {"name": name}) and (
            event_type is None or event_type in subscriber["event_types"]
        )
    ]
    return jsonify(paginate(items))


@app.get("/api/subscribers/<subscriber_id>")
def get_subscriber(subscriber_id):
    subscriber = subscribers.get(subscriber_id)
    if not subscriber:
        return jsonify({"error": "Subscriber not found"}), 404
    return jsonify(subscriber)


@app.put("/api/subscribers/<subscriber_id>")
def update_subscriber(subscriber_id):
    subscriber = subscribers.get(subscriber_id)
    if not subscriber:
        return jsonify({"error": "Subscriber not found"}), 404

    body = json_body()
    for field in ["name", "event_types", "callback_url", "secret"]:
        if field in body:
            subscriber[field] = body[field]

    return jsonify(subscriber)


@app.delete("/api/subscribers/<subscriber_id>")
def delete_subscriber(subscriber_id):
    subscriber = subscribers.pop(subscriber_id, None)
    if not subscriber:
        return jsonify({"error": "Subscriber not found"}), 404
    return jsonify({"message": "Subscriber deleted", "id": subscriber_id})


@app.post("/api/events")
def publish_event():
    body = json_body()
    event_type = body.get("type")
    data = body.get("data")

    if not event_type or data is None:
        return jsonify({"error": "Fields 'type' and 'data' are required"}), 400

    notification = create_notification(event_type, data)
    matched_subscribers = [
        subscriber for subscriber in subscribers.values() if event_type in subscriber["event_types"]
    ]

    payload = {
        "event_id": new_id("evt"),
        "type": event_type,
        "occurred_at": utc_now(),
        "data": data,
        "notification_id": notification["id"],
    }

    delivery_results = [
        send_webhook(subscriber, event_type, payload, notification["id"])
        for subscriber in matched_subscribers
    ]

    notification["status"] = "delivered" if delivery_results else "ignored"

    return jsonify(
        {
            "notification": notification,
            "delivery_count": len(delivery_results),
            "deliveries": delivery_results,
        }
    ), 202


@app.get("/api/notifications")
def list_notifications():
    event_type = request.args.get("event_type")
    status = request.args.get("status")
    subscriber_id = request.args.get("subscriber_id")

    items = list(notifications.values())
    items = [
        item for item in items if matches_filters(item, {"event_type": event_type, "status": status})
    ]

    if subscriber_id is not None:
        notification_ids = {
            delivery["notification_id"]
            for delivery in deliveries.values()
            if delivery["subscriber_id"] == subscriber_id
        }
        items = [item for item in items if item["id"] in notification_ids]

    return jsonify(paginate(items))


@app.get("/api/notifications/<notification_id>")
def get_notification(notification_id):
    notification = notifications.get(notification_id)
    if not notification:
        return jsonify({"error": "Notification not found"}), 404
    return jsonify(notification)


@app.get("/api/deliveries")
def list_deliveries():
    filters = {
        "status": request.args.get("status"),
        "subscriber_id": request.args.get("subscriber_id"),
        "notification_id": request.args.get("notification_id"),
        "event_type": request.args.get("event_type"),
    }

    items = [delivery for delivery in deliveries.values() if matches_filters(delivery, filters)]
    return jsonify(paginate(items))


@app.get("/api/deliveries/<delivery_id>")
def get_delivery(delivery_id):
    delivery = deliveries.get(delivery_id)
    if not delivery:
        return jsonify({"error": "Delivery not found"}), 404
    return jsonify(delivery)


@app.post("/api/deliveries/<delivery_id>/retry")
def retry_delivery(delivery_id):
    original = deliveries.get(delivery_id)
    if not original:
        return jsonify({"error": "Delivery not found"}), 404

    subscriber = subscribers.get(original["subscriber_id"])
    notification = notifications.get(original["notification_id"])
    if not subscriber or not notification:
        return jsonify({"error": "Cannot retry because dependency is missing"}), 409

    payload = {
        "event_id": new_id("evt"),
        "type": notification["event_type"],
        "occurred_at": utc_now(),
        "data": notification["data"],
        "notification_id": notification["id"],
        "retry_of": delivery_id,
    }
    redelivery = send_webhook(
        subscriber,
        notification["event_type"],
        payload,
        notification["id"],
        retry_of=delivery_id,
    )
    return jsonify(redelivery), 202


@app.post("/webhooks/demo-receiver")
def demo_receiver():
    raw_body = request.get_data()
    signature = request.headers.get("X-Webhook-Signature", "")
    event_type = request.headers.get("X-Webhook-Event", "")
    delivery_id = request.headers.get("X-Webhook-Delivery", "")
    subscriber_id = request.headers.get("X-Webhook-Subscriber", "")

    body = json.loads(raw_body.decode("utf-8") or "{}")
    secret = subscribers.get(subscriber_id, {}).get("secret")

    if not secret:
        return jsonify({"error": "No subscriber secret available"}), 400

    expected_signature = build_signature(secret, raw_body)
    verified = hmac.compare_digest(signature, expected_signature)

    received = {
        "delivery_id": delivery_id,
        "event_type": event_type,
        "verified": verified,
        "received_at": utc_now(),
        "payload": body,
    }
    received_webhooks.append(received)

    if not verified:
        return jsonify({"status": "rejected", "reason": "invalid signature"}), 400

    return jsonify({"status": "accepted", "received": received}), 200


@app.get("/webhooks/demo-receiver/logs")
def receiver_logs():
    return jsonify({"items": received_webhooks, "total": len(received_webhooks)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)