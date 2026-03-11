from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

book_data = [
	{"id": 1, "title": "Clean Code", "category": "IT"},
	{"id": 2, "title": "How to learn", "category": "self-help"}
]

# non consistency
@app.route("/api/v1/get-books", methods=["GET"])
def get_books():
  return jsonify(book_data)

@app.route("/api/v1/books/<int:id>", methods=["GET"])
def get_book(id):
  for book in book_data:
    if book["id"] == id:
      return jsonify(book), 200
  return {"error": "Book not found"}, 404

# consistency
@app.route("/books/v1/<int:id>", methods=["PUT"])
def update_book(id):
  data = request.json
  for book in book_data:
    if book["id"] == id:
      book["title"] = data["title"]
      book["category"] = data["category"]
      
      return jsonify({
        "message": "Book updated",
        "book": book
      }), 200
  return {"error": "Book not found"}, 404

@app.route("/api/v1/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
  for book in book_data:
      if book["id"] == book_id:

        book_data.remove(book)

        return jsonify({
            "message": "Book deleted"
        })

  return {"error": "Book not found"}, 404

if __name__ == "__main__":
    app.run(debug=True)


