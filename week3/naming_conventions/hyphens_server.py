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

# example bad: camelCase
@app.route("/api/v1/bookList", methods=["GET"])
def get_book_wrong():
    return jsonify(
		{
			"data": book_data
		}
	)

# example bad: underscore
@app.route("/api/v1/book_info/<int:id>", methods=["GET"])
def get_book_by_id_wrong(id):
	book = next((b for b in book_data if b["id"] == id), None)
	if not book:
		return jsonify({"error": "Book not found"}), 404
    
	return jsonify({"data": book}), 200
    
# example good: hyphen
@app.route("/api/v1/book-list", methods=["GET"])
def get_books():
    return jsonify(
		{
			"data": book_data
		}
	)
    
@app.route("/api/v1/book-info/<int:id>", methods=["GET"])
def get_book_by_id(id):
    book = next((b for b in book_data if b["id"] == id), None)
        
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    return jsonify({"data": book}), 200

if __name__ == "__main__":
  	app.run(debug=True)
