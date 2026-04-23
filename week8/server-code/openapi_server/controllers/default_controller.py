import connexion

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

from openapi_server.database import get_books_collection
from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.book_input import BookInput  # noqa: E501
from openapi_server.models.delete_response import DeleteResponse  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server import util

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _book_doc_to_response(doc: dict) -> Book:
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "author": doc.get("author"),
        "price": doc.get("price"),
        "publishedYear": doc.get("publishedYear"),
        "createdAt": doc.get("createdAt"),
        "updatedAt": doc.get("updatedAt"),
    }
    
def _bad_request(message: str):
    return {"message": message}, 400


def _not_found(message: str):
    return {"message": message}, 404


def _internal_error(message: str = "Internal server error"):
    return {"message": message}, 500
    
def books_get():  # noqa: E501
    try:
        collection = get_books_collection()
        docs = collection.find().sort("_id", -1)

        books = [_book_doc_to_response(doc) for doc in docs]
        return books, 200

    except PyMongoError:
        return _internal_error()


def books_id_delete(id_):  # noqa: E501
    """Delete book"""
    try:
        try:
            object_id = ObjectId(id_)
        except InvalidId:
            return _bad_request("Invalid book id")

        collection = get_books_collection()
        result = collection.delete_one({"_id": object_id})

        if result.deleted_count == 0:
            return _not_found("Book not found")

        return {"message": "Deleted successfully"}, 200

    except PyMongoError:
        return _internal_error()


def books_id_get(id_):  # noqa: E501
    """
    Get book by id
    """
    try:
        collection = get_books_collection()

        try:
            object_id = ObjectId(id_)
        except InvalidId:
            return _bad_request("Invalid book id")

        doc = collection.find_one({"_id": object_id})
        if not doc:
            return _not_found("Book not found")

        return _book_doc_to_response(doc), 200

    except PyMongoError:
        return _internal_error()


def books_id_put(id_, body):  # noqa: E501
    """Update book"""
    try:
        try:
            object_id = ObjectId(id_)
        except InvalidId:
            return _bad_request("Invalid book id")

        book_input = body
        if connexion.request.is_json:
            book_input = BookInput.from_dict(connexion.request.get_json())  # noqa: E501

        title = getattr(book_input, "title", None)
        author = getattr(book_input, "author", None)
        price = getattr(book_input, "price", None)
        published_year = getattr(book_input, "published_year", None)

        if not title or not author:
            return _bad_request("title and author are required")

        update_data = {
            "title": title,
            "author": author,
            "price": price,
            "publishedYear": published_year,
            "updatedAt": _utc_now_iso(),
        }

        collection = get_books_collection()
        result = collection.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return _not_found("Book not found")

        updated_doc = collection.find_one({"_id": object_id})
        return _book_doc_to_response(updated_doc), 200

    except PyMongoError:
        return _internal_error()


def books_post(body):  # noqa: E501
    """Create book"""
    try:
        book_input = body
        if connexion.request.is_json:
            book_input = BookInput.from_dict(connexion.request.get_json())  # noqa: E501

        title = getattr(book_input, "title", None)
        author = getattr(book_input, "author", None)
        price = getattr(book_input, "price", None)
        published_year = getattr(book_input, "published_year", None)

        if not title or not author:
            return _bad_request("title and author are required")

        now = _utc_now_iso()
        doc = {
            "title": title,
            "author": author,
            "price": price,
            "publishedYear": published_year,
            "createdAt": now,
            "updatedAt": now,
        }

        collection = get_books_collection()
        result = collection.insert_one(doc)

        created_doc = collection.find_one({"_id": result.inserted_id})
        return _book_doc_to_response(created_doc), 201

    except PyMongoError:
        return _internal_error()
