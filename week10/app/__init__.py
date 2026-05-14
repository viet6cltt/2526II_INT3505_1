from flask import Flask, Response, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .extensions import db, limiter, metrics
from .routes import register_routes
from .config import Config
from .logging_config import register_request_logging, setup_logging
from .tracing import setup_tracing

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    setup_logging(app)
    setup_tracing(app, "auth-service")
    register_request_logging(app)
    
    limiter.init_app(app)
    
    metrics.init_app(app)
    
    @app.route('/metrics')
    @limiter.exempt
    def prometheus_metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    
    db.init_app(app)
    register_routes(app)

    return app
