import os
import time

from flask import Flask, jsonify, request
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace


def setup_tracing(app):
    endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
        "http://127.0.0.1:4318/v1/traces",
    )
    resource = Resource.create({"service.name": "notification-service"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)
    FlaskInstrumentor().instrument_app(app, excluded_urls="/health")


app = Flask(__name__)
setup_tracing(app)


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/notify/welcome")
def send_welcome_notification():
    data = request.get_json() or {}
    delay_seconds = float(os.getenv("NOTIFICATION_DELAY_SECONDS", "0.2"))
    should_fail = os.getenv("NOTIFICATION_FORCE_FAIL", "false").lower() == "true"

    time.sleep(delay_seconds)

    if should_fail:
        return jsonify({"error": "Notification provider failed"}), 503

    return jsonify({
        "message": "Welcome notification sent",
        "data": {
            "user_id": data.get("user_id"),
            "username": data.get("username"),
            "email": data.get("email"),
        }
    }), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
