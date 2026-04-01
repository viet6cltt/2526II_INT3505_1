from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy import Enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    role = db.Column(Enum(UserRole), default=UserRole.USER)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value
        }