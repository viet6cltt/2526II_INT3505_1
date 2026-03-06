from flask import Flask, jsonify

app = Flask(__name__)

students = [
    {"id": 1, "name": "An"},
    {"id": 2, "name": "Binh"},
    {"id": 3, "name": "Cuong"}
]

@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students)

@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    for s in students:
        if s["id"] == id:
            return jsonify(s)
    return {"error": "Student not found"}, 404

if __name__ == "__main__":
    app.run(debug=True)