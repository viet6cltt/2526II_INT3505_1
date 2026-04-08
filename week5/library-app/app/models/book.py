from ..extensions import db

class Book(db.Model):
    __tablename__ = "books"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    # category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    
    # category = db.relationship("Category")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.title,
            # "category":
            #     {
            #         "id": self.category_id,
            #         "name": self.category.name
            #     }
        }