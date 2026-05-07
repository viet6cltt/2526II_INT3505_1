from flask import Flask, Blueprint, request, jsonify
from ..extensions import db
from ..models.user import User

user_bp = Blueprint("users", __name__)

@user_bp.route("", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(name=data.get("name"), email=data.get("email"))
    
    exising_user = User.query.filter_by(email=user.email).first()
    if exising_user:
        return jsonify({"message": "Email already exists"}), 400
    
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201