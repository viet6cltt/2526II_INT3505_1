from flask import Blueprint, request, jsonify
from datetime import datetime
from ..extensions import db
from ..models.borrow_record import BorrowRecord
from ..models.user import User
from ..models.book import Book

borrow_bp = Blueprint("borrows", __name__)

@borrow_bp.route("", methods=["GET"])
def get_borrow_records():
    search = request.args.get("search")
    cursor = request.args.get("cursor")
    limit = request.args.get("pageSize", 10, type=int)
    
    if limit <= 0:
        limit = 10
    if limit > 100:
        limit = 100
    
    query = BorrowRecord.query.join(User).join(Book)
    
    if search:
        query  = query.filter(
            db.or_(
                User.name.contains(search),
                Book.title.contains(search)
            )
        )
        
    query = query.order_by(BorrowRecord.id.desc())
    
    if cursor is not None:
        query = query.filter(BorrowRecord.id < cursor)
        
    
    records = query.limit(limit + 1).all()
    
    has_next = len(records) > limit
    records = records[:limit]
    
    next_cursor = records[-1].id if has_next and records else None
    
    return jsonify({
        "data": [record.to_dict() for record in records],
        "metadata": {
            "limit": limit,
            "nextCursor": next_cursor,
            "hasNext": has_next
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
        return jsonify({"message": "User or Book not found"}), 404
    
    # check if the book is already borrowed
    existing_borrow= BorrowRecord.query.filter_by(
        user_id = user_id,
        book_id = book_id,
        return_date = None
    ).first()
    
    if existing_borrow:
        return jsonify({"message": "This user is already borrowing this book"}), 400
    
    borrow_record = BorrowRecord(user_id=user_id, book_id=book_id, borrow_date=datetime.now())
    db.session.add(borrow_record)
    db.session.commit()
    
    return jsonify(borrow_record.to_dict()), 201

@borrow_bp.route("/<int:id>", methods=["PUT"])
def return_book(id):
    record = BorrowRecord.query.get(id)

    if not record:
        return jsonify({"message": "Borrow record not found"}), 404

    if record.return_date is not None:
        return jsonify({"message": "Book has already been returned"}), 400

    record.return_date = datetime.now()
    db.session.commit()

    return jsonify({
        "message": "Book returned successfully",
        "data": record.to_dict()
    })

@borrow_bp.route("/<int:id>", methods=["DELETE"])
def delete_borrow_record(id):
    record = BorrowRecord.query.get(id)

    if not record:
        return jsonify({"message": "Borrow record not found"}), 404

    db.session.delete(record)
    db.session.commit()

    return jsonify({"message": "Borrow record deleted successfully"})
    