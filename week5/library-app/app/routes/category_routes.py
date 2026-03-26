from flask import Blueprint, request, jsonify
from ..models.category import Category
from ..extensions import db

category_bp = Blueprint("categories", __name__)

@category_bp.route("", methods=["GET"])
def get_categories():
    search = request.args.get("search")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("pageSize", 10))
    
    query = Category.query
    
    if search:
        query = query.filter(Category.name.contains(search))
        
    pagination = query.paginate(page = page, per_page=page_size, error_out=False)
    
    return jsonify({
        "data": [category.to_dict() for category in pagination.items],
        "metadata": {
            "page": page,
            "pageSize": page_size,
            "total": pagination.total,
            "totalPages": pagination.pages
        }
    })

@category_bp.route("", methods=["POST"])
def create_category():
    data = request.get_json()
    name = data.get("name")
    
    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return jsonify({"message": "Category name already exists"}), 400
    
    
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    
    
    return jsonify(category.to_dict()), 201