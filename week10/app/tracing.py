import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Tránh cấu hình lại nhiều lần 
_configured = False


def setup_tracing(app, service_name):
    global _configured

    # set up tracing chỉ khi chưa được cấu hình 
    if not _configured:
        # enpoint mà OTLP exporter gửi trace đến
        endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            "http://127.0.0.1:4318/v1/traces",
        )
        # metadata
        # gắn service name vào resource để phân biệt trace từ các service khác nhau
        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        # cấu hình để gửi trace đến OTLP endpoint
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        trace.set_tracer_provider(provider)
        RequestsInstrumentor().instrument()
        _configured = True

    # không trace /metrics 
    FlaskInstrumentor().instrument_app(app, excluded_urls="/metrics")
