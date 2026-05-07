from ..extensions import db

class Book(db.Model):
    __tablename__ = "books"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.title,
        }