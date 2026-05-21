from flask import Flask

from routes import notifications_bp


app = Flask(__name__)
app.register_blueprint(notifications_bp)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
