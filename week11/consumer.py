import json
import os
from datetime import datetime, UTC

import pika


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "notification_events")
EVENT_LOG_FILE = os.path.join(os.path.dirname(__file__), "event_logs.jsonl")


def append_event_log(event_name, payload):
    log_entry = {
        "event_name": event_name,
        "payload": payload,
        "source": "consumer",
        "publish_status": "handled",
        "created_at": datetime.now(UTC).isoformat(),
    }
    with open(EVENT_LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")


def handle_event(channel, method, properties, body):
    event = json.loads(body)
    event_name = event["event_name"]
    payload = event["payload"]

    print(f"[consumer] handled {event_name}: {payload}", flush=True)
    append_event_log(event_name, payload)


def main():
    print(
        f"[consumer] connecting to {RABBITMQ_HOST}/{RABBITMQ_QUEUE}",
        flush=True,
    )
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=False)
    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=handle_event,
        auto_ack=True,
    )

    print(f"[consumer] connected to {RABBITMQ_HOST}", flush=True)
    print(f"[consumer] waiting for events in '{RABBITMQ_QUEUE}'", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
