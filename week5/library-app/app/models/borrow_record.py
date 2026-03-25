from ..extensions import db
from datetime import datetime

class BorrowRecord(db.Model):
    __tablename__ = "borrow_records"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"))
    borrow_date = db.Column(db.DateTime, default=datetime.now)
    return_date = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship("User")
    book = db.relationship("Book")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "book": self.book,
            "borrowDate": self.borrow_date,
            "returnDate": self.return_date
        }