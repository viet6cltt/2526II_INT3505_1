from flask import Flask, request, jsonify

app = Flask(__name__)

book_data = [
    {"id": 1, "title": "Clean Code", "category": "IT", "author": "Robert C. Martin"},
    {"id": 2, "title": "How to Learn", "category": "self-help", "author": "Unknown"},
    {"id": 3, "title": "Something", "category": "IT", "author": "Robert C. Martin"},
    {"id": 4, "title": "Blean Code", "category": "IT", "author": "Robert C. Martin"},
    {"id": 5, "title": "Plean Code", "category": "IT", "author": "Robert C. Martin"},
    {"id": 6, "title": "Alean Code", "category": "IT", "author": "Robert C. Martin"},
    {"id": 7, "title": "Jlean Code", "category": "IT", "author": "Robert C. Martin"}
]

def find_book(book_id):
    return next((b for b in book_data if b["id"] == book_id), None)


# API v1
@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book_v1(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    return jsonify(
        {
            "data": {
                "id": book["id"],
                "title": book["title"],
                "category": book["category"]
            }
        }
    )

# API v2: extensibility - thêm field
@app.route("/api/v2/books/<int:book_id>", methods=["GET"])
def get_book_v2(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"error": "BBook not found"}), 404
    
    return jsonify(
        {
            "data": {
                "id": book["id"],
                "title": book["title"],
                "category": book["category"],
                "author": book["author"] 
        }
        }
    )

# List API: extensibility qua filter & pagination, sort
@app.route("/api/v2/books", methods=["GET"])
def list_books_v2():
    results = book_data.copy()
    
    category = request.args.get("category")
    sort_by = request.args.get("sort", default="id")
    
    if category:
        results = [b for b in book_data if b["category"] == category]
        
    author = request.args.get("author")
    if author: 
        results = [b for b in book_data if b["author"] == author]
    
    # pagination
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 4))
    
    start = (page - 1) * limit
    end = start + limit
    
    paginated_results = sorted(results[start:end], key=lambda book: book[sort_by])
    
    return jsonify({
        "metadata": {
            "total": len(results),
            "page": page,
            "limit": limit
        },
        "data": paginated_results
    })

if __name__ == "__main__":
    app.run(debug=True)