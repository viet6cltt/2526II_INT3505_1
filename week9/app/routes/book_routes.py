from flask import Blueprint, request, jsonify
from ..models.book import Book
from ..extensions import db

book_bp = Blueprint("books", __name__)

@book_bp.route("", methods=["GET"])
def get_books():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))
    
    if page_size <= 10:
        page_size = 10
    if page_size > 100:
        page_size = 100
        
    query = Book.query
    pagination  = query.paginate(page = page, per_page=page_size, error_out=False)
    
    return jsonify({
        "data": [book.to_dict() for book in pagination.items],
        "metadata": {
            "page": page,
            "pageSize": page_size,
            "total": pagination.total,
            "totalPages": pagination.pages
        }
    })
    
@book_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@book_bp.route("", methods=["POST"])
def create_book():
    data = request.get_json()   
    
    book = Book(
        title=data.get("title"),
        category_id=data.get("categoryId")
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201