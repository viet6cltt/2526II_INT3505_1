from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

book_data = [
	{"id": 1, "title": "Clean Code", "category": "IT"},
	{"id": 2, "title": "How to learn", "category": "self-help"}
]

# non clarity
'''
	- endpoint mơ hồ
	- parameter mơ hồ
	- response mơ hồ
'''
@app.route("/api/v1/data", methods=["GET"])
def get_data():
    t = request.args.get("t", type=int)
    for b in book_data:
        if b["id"] == t:
            return jsonify({
                "i": b["id"],
                "t": b["title"]
            }), 200
    return jsonify({"e": "not found"}), 404

# clarity
'''
	- endpoint rõ ràng
	- parameter rõ ràng
	- response rõ ràng
'''
@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    for b in book_data:
        if b["id"] == book_id:
            return jsonify({
                "data": {
                    "id": b["id"],
                    "title": b["title"],
                    "category": b["category"]
                }
            }), 200
    return jsonify({
        "error": {
            "message": "Book not found"
        }
    }), 404

if __name__ == "__main__":
    app.run(debug=True)


