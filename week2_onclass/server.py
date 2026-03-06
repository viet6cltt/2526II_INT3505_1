from flask import Flask, jsonify

app = Flask(__name__)

students = [
    {"id": 1, "name": "An"},
    {"id": 2, "name": "Binh"},
    {"id": 3, "name": "Cuong"}
]

# GET all students
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students), 200


# GET one student
@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    for s in students:
        if s["id"] == id:
            return jsonify(s), 200
    return {"message": "Student not found"}, 404


# CREATE student
@app.route("/students", methods=["POST"])
def add_student():
    data = request.json
    students.append(data)
    return jsonify(data), 201


# UPDATE student
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.json
    for s in students:
        if s["id"] == id:
            s["name"] = data["name"]
            return jsonify(s), 200
    return {"message": "Student not found"}, 404


# DELETE student
@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    global students
    students = [s for s in students if s["id"] != id]
    return {"message": "Deleted"}, 200


if __name__ == "__main__":
    app.run(debug=True)