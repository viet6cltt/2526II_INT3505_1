from ..extensions import db

class Book(db.Model):
    __tablename__ = "books"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.Foreign_key("categories.id"))
    author_id = db.Column(db.Integer, db.Foreign_key("authors.id"))
    
