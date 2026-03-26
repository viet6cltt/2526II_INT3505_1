from .book_routes import book_bp
from .category_routes import category_bp
from .borrow_routes import borrow_bp

def register_routes(app):
    app.register_blueprint(book_bp, url_prefix="/books")
    app.register_blueprint(category_bp, url_prefix="/categories")
    app.register_blueprint(borrow_bp, url_prefix="/borrows")