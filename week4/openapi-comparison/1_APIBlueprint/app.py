from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route("/api-docs")
def docs():
    return send_from_directory('static', 'api-docs.html')

if __name__ == "__main__":
    app.run(debug=True)