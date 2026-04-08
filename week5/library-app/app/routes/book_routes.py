from flask import Blueprint, request, jsonify
from ..models.book import Book
from ..extensions import db

book_bp = Blueprint("books", __name__)

# @book_bp.route("", methods=["GET"])
# def get_books():
#     search = request.args.get("search")
#     page = int(request.args.get("page", 1))
#     page_size = int(request.args.get("pageSize", 10))
    
#     query = Book.query
    
#     if search:
#         query = query.filter(Book.title.contains(search))
        
#     pagination = query.paginate(page = page, per_page=page_size, error_out=False)
    
#     return jsonify({
#         "data": [book.to_dict() for book in pagination.items],
#         "metadata": {
#             "page": page,
#             "pageSize": page_size,
#             "total": pagination.total,
#             "totalPages": pagination.pages
#         }
#     })


@book_bp.route("", methods=["GET"])
def get_books():
    type = request.args.get("type", "page-based")
    if type == "page-based":
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("pageSize", 10))
        
        if page_size <= 10:
            page_size = 10
        if page_size > 100:
            page_size = 100
        query = Book.query

        pagination = query.paginate(page = page, per_page=page_size, error_out=False)
        
        return jsonify({
            "data": [book.to_dict() for book in pagination.items],
            "metadata": {
                "type": "page-based",
                "page": page,
                "pageSize": page_size,
                "total": pagination.total,
                "totalPages": pagination.pages
            }
        })
    elif type == "cursor-based":
        cursor = request.args.get("cursor")
        limit = int(request.args.get("pageSize", 10))
        
        if limit <= 0: 
            limit = 10
        if limit > 100:
            limit = 100
        
        query = Book.query.order_by(Book.id.desc())
        
        if cursor:
            query = query.filter(Book.id < cursor)
            
        records = query.limit(limit + 1).all()
        
        has_next = len(records) > limit
        records = records[:limit]
        
        next_cursor = records[-1].id if has_next and records else None
        
        return jsonify({
            "data": [book.to_dict() for book in records],
            "metadata": {
                "type": "cursor-based",
                "pageSize": limit,
                "nextCursor": next_cursor,
                "hasNext": has_next
            }
        })
    else:
        return jsonify({"error": "Invalid pagination type"}), 400
        
    
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
