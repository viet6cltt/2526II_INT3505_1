from .versioning_demo_routes import versioning_demo_bp

def register_routes(app):
    app.register_blueprint(versioning_demo_bp)
