from flask import Flask, request, jsonify

app = Flask(__name__)

book_data_v1 = [
    {"id": 1, "title": "Clean Code", "category": "IT"},
    {"id": 2, "title": "How to Learn", "category": "self-help"},
    {"id": 3, "title": "Something", "category": "IT"},
    {"id": 4, "title": "Blean Code", "category": "IT"},
    {"id": 5, "title": "Plean Code", "category": "IT"},
    {"id": 6, "title": "Alean Code", "category": "IT"},
    {"id": 7, "title": "Jlean Code", "category": "IT"}
]

book_data_v2 = [
    {"id": 1, "title": "Clean Code", "category": "IT", "author": "Robert C. Martin"},
    {"id": 2, "title": "How to Learn", "category": "self-help", "author": "Unknown"},
    {"id": 3, "title": "Something", "category": "IT", "author": "Robert C. Martin"},
    {"id": 4, "title": "Blean Code", "category": "IT", "author": "Robert C. Martin"},
    {"id": 5, "title": "Plean Code", "category": "IT", "author": "Robert C. Martin"},
    {"id": 6, "title": "Alean Code", "category": "IT", "author": "Robert C. Martin"},
    {"id": 7, "title": "Jlean Code", "category": "IT", "author": "Robert C. Martin"}
]

# API v1
@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book_v1(book_id):
    book = next((b for b in book_data_v1 if b["id"] == book_id), None)
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

# API v2: versioning
@app.route("/api/v2/books/<int:book_id>", methods=["GET"])
def get_book_v2(book_id):
    book = next((b for b in book_data_v2 if b["id"] == book_id), None)
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


if __name__ == "__main__":
    app.run(debug=True)