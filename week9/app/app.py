from flask import Flask
from .extensions import db
from models import db
from routes import regiter_routes


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

regiter_routes(app)


if __name__ == '__main__':
    app.run(debug=True)