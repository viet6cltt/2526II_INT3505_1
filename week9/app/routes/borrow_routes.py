from flask import Blueprint, request, jsonify
from datetime import datetime
from ..extensions import db
from ..models.borrow_record import BorrowRecord
from ..models.user import User
from ..models.book import Book

borrow_bp = Blueprint("borrows", __name__)

@borrow_bp.route("", methods=["GET"])
def get_borrow_records():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))
    
    if page_size <= 10:
        page_size = 10
    if page_size > 100:
        page_size = 100
    
    query = BorrowRecord.query.join(User).join(Book)
    
    pagination = query.paginate(page = page, per_page=page_size, error_out=False)
    
    return jsonify({
        "data": [record.to_dict() for record in pagination.items],
        "metadata": {
            "page": page,
            "pageSize": page_size,
            "total": pagination.total,
            "totalPages": pagination.pages
        }
    })  
    
@borrow_bp.route("", methods=["POST"])
def create_borrow_record():
    data = request.get_json()
    user_id = data.get("userId")
    book_id = data.get("bookId")
    
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    
    if not user or not book:
        return jsonify({"error": "User or Book not found"}), 404
    
    # check if the book is already borrowed
    existing_borrow= BorrowRecord.query.filter_by(
        user_id = user_id,
        book_id = book_id,
        return_date = None
    ).first()
    
    if existing_borrow:
        return jsonify({"message": "This user is already borrowing this book"}), 400
    
    borrow_record = BorrowRecord(
        user_id=user_id,
        book_id=book_id,
        borrow_date=datetime.now()
    )
    
    db.session.add(borrow_record)
    db.session.commit()
    
    return jsonify(borrow_record.to_dict()), 201

@borrow_bp.route("/<int:id>", methods=["DELETE"])
def delete_borrow_record(id):
    record = BorrowRecord.query.get(id)

    if not record:
        return jsonify({"message": "Borrow record not found"}), 404

    db.session.delete(record)
    db.session.commit()

    return jsonify({"message": "Borrow record deleted successfully"})