from flask import Flask, jsonify, request
import jwt
import datetime

app = Flask(__name__)

students = [
    {"id": 1, "name": "An", "password": "123"},
    {"id": 2, "name": "Binh", "password": "123"},
    {"id": 3, "name": "Cuong", "password": "123"}
]

# GET all students
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students), 200


# GET one student
@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):
    user = verify_token()
    if not user:
        return {"message": "Unauthorized"}, 401
    for s in students:
        if s["id"] == id:
            return jsonify(s), 200
    return {"message": "Student not found"}, 404


# CREATE student
@app.route("/students", methods=["POST"])
def add_student():
    user = verify_token()
    if not user:
        return {"message": "Unauthorized"}, 401
    data = request.json
    students.append(data)
    return jsonify(data), 201


# UPDATE student
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    user = verify_token()
    if not user:
        return {"message": "Unauthorized"}, 401
    data = request.json
    for s in students:
        if s["id"] == id:
            s["name"] = data["name"]
            return jsonify(s), 200
    return {"message": "Student not found"}, 404


# DELETE student
@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    user = verify_token()
    if not user:
        return {"message": "Unauthorized"}, 401
    global students
    students = [s for s in students if s["id"] != id]
    return {"message": "Deleted"}, 200


# Login
SECRET_KEY = "secret"

@app.route("/login", methods=["POST"])
def login():
    data = request.json

    for s in students:
        if s["name"] == data["name"] and s["password"] == data["password"]:
            token = jwt.encode(
                {
                    "user": s["name"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                },
                SECRET_KEY,
                algorithm="HS256"
            )

            return jsonify({"token": token})

    return {"message": "Invalid credentials"}, 401

def verify_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    parts = auth_header.split(" ")
    if len(parts) != 2:
        return None

    token = parts[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None



if __name__ == "__main__":
    app.run(debug=True)