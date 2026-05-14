from flask import Flask

from .extensions import db, limiter
from .routes import register_routes
from .config import Config

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    limiter.init_app(app)
    
    db.init_app(app)
    register_routes(app)

    return app