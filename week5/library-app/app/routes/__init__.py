from .book_routes import book_bp

def register_routes(app):
    app.register_blueprint(book_bp, url_prefix="/books")