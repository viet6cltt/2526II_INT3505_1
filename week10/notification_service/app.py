import os
import sys
import time
import logging
import importlib.util

from flask import Flask, jsonify, request

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry import trace


LOGGING_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "logging_config.py")
)
logging_config_spec = importlib.util.spec_from_file_location(
    "week10_logging_config",
    LOGGING_CONFIG_PATH,
)
logging_config = importlib.util.module_from_spec(logging_config_spec)
sys.modules[logging_config_spec.name] = logging_config
logging_config_spec.loader.exec_module(logging_config)
register_request_logging = logging_config.register_request_logging
setup_logging = logging_config.setup_logging

logger = logging.getLogger(__name__)


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
app.config["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")
app.config["LOG_FORMAT"] = os.getenv("LOG_FORMAT", "json")
app.config["WERKZEUG_LOG_LEVEL"] = os.getenv("WERKZEUG_LOG_LEVEL", "WARNING")
setup_logging(app)
setup_tracing(app)
register_request_logging(app)


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/notify/welcome")
def send_welcome_notification():
    data = request.get_json() or {}
    delay_seconds = float(os.getenv("NOTIFICATION_DELAY_SECONDS", "0.2"))
    should_fail = os.getenv("NOTIFICATION_FORCE_FAIL", "false").lower() == "true"

    logger.info(
        "welcome notification requested",
        extra={"user_id": data.get("user_id"), "username": data.get("username")},
    )
    time.sleep(delay_seconds)

    if should_fail:
        logger.error(
            "welcome notification provider failed",
            extra={"user_id": data.get("user_id")},
        )
        return jsonify({"error": "Notification provider failed"}), 503

    logger.info(
        "welcome notification completed",
        extra={"user_id": data.get("user_id"), "username": data.get("username")},
    )
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
