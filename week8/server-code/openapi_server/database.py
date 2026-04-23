import os
from pathlib import Path

from pymongo import MongoClient
from pymongo.errors import PyMongoError

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


_BASE_DIR = Path(__file__).resolve().parent
_ENV_PATH = _BASE_DIR / ".env"

if load_dotenv is not None:
    load_dotenv(_ENV_PATH)


_mongo_client = None
_mongo_database = None


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_mongo_client() -> MongoClient:
    global _mongo_client

    if _mongo_client is None:
        mongo_uri = _get_required_env("MONGO_URI")
        _mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    return _mongo_client


def get_database():
    global _mongo_database

    if _mongo_database is None:
        database_name = _get_required_env("MONGO_DB_NAME")
        _mongo_database = get_mongo_client()[database_name]

    return _mongo_database


def get_books_collection():
    return get_database()["books"]


def ping_database() -> bool:
    try:
        get_mongo_client().admin.command("ping")
        return True
    except PyMongoError:
        return False
