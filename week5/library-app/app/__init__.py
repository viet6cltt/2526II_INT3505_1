from flask import Flask
from .extensions import db
from .routes import register_routes
from flask.cli import with_appcontext
from app.models.book import Book


def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    register_routes(app)
    
    # command 
    
    @app.cli.command("seed-data")
    @with_appcontext
    def seed_data():
        batch_size = 10000
        total = 1_000_000

        books = []
        for i in range(1, total + 1):
            books.append(Book(title=f"Book {i}"))
            
            if len(books) >= batch_size:
                db.session.bulk_save_objects(books)
                db.session.commit()
                books = []
                print(f"Inserted {i} books")
            
        if books: # Insert remaining books
            db.session.bulk_save_objects(books)
            db.session.commit()
            print(f"Inserted {total} books")
        print(f"Done inserting {total} books")
        
    return app


