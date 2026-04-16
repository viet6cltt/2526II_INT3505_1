from __future__ import annotations

from typing import Any, Dict, List, Optional

from pymongo.collection import Collection
from pymongo.database import Database


class ProductModel:
    COLLECTION_NAME = "products"
    COUNTERS_COLLECTION = "counters"
    COUNTER_KEY = "product_id"

    REQUIRED_FIELDS = ["name", "description", "price", "stock", "category"]

    @staticmethod
    def _collection(db: Database) -> Collection:
        return db[ProductModel.COLLECTION_NAME]

    @staticmethod
    def _counters_collection(db: Database) -> Collection:
        return db[ProductModel.COUNTERS_COLLECTION]

    @staticmethod
    def _get_next_id(db: Database) -> int:
        result = ProductModel._counters_collection(db).find_one_and_update(
            {"_id": ProductModel.COUNTER_KEY},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=True,
        )
        return int(result["seq"])

    @staticmethod
    def validate_payload(payload: Dict[str, Any], partial: bool = False) -> Optional[str]:
        if not isinstance(payload, dict):
            return "Payload must be a JSON object"

        if not partial:
            for field in ProductModel.REQUIRED_FIELDS:
                if field not in payload:
                    return f"Missing required field: {field}"

        if "name" in payload and not isinstance(payload["name"], str):
            return "Field 'name' must be a string"

        if "description" in payload and not isinstance(payload["description"], str):
            return "Field 'description' must be a string"

        if "category" in payload and not isinstance(payload["category"], str):
            return "Field 'category' must be a string"

        if "price" in payload:
            if not isinstance(payload["price"], (int, float)):
                return "Field 'price' must be a number"
            if payload["price"] < 0:
                return "Field 'price' must be >= 0"

        if "stock" in payload:
            if not isinstance(payload["stock"], int):
                return "Field 'stock' must be an integer"
            if payload["stock"] < 0:
                return "Field 'stock' must be >= 0"

        return None

    @staticmethod
    def to_list_item(doc: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": doc["id"],
            "name": doc["name"],
            "price": float(doc["price"]),
            "category": doc["category"],
        }

    @staticmethod
    def to_detail(doc: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": doc["id"],
            "name": doc["name"],
            "description": doc["description"],
            "price": float(doc["price"]),
            "stock": int(doc["stock"]),
            "category": doc["category"],
        }

    @staticmethod
    def create(db: Database, payload: Dict[str, Any]) -> Dict[str, Any]:
        new_doc = {
            "id": ProductModel._get_next_id(db),
            "name": payload["name"].strip(),
            "description": payload["description"].strip(),
            "price": float(payload["price"]),
            "stock": int(payload["stock"]),
            "category": payload["category"].strip(),
        }

        ProductModel._collection(db).insert_one(new_doc)
        return new_doc

    @staticmethod
    def find_all(
        db: Database,
        page: int = 1,
        limit: int = 10,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        query: Dict[str, Any] = {}

        if category:
            query["category"] = category

        if search:
            query["name"] = {"$regex": search, "$options": "i"}

        skip = (page - 1) * limit

        cursor = (
            ProductModel._collection(db)
            .find(query, {"_id": 0})
            .sort("id", 1)
            .skip(skip)
            .limit(limit)
        )

        data = [ProductModel.to_list_item(doc) for doc in cursor]
        total = ProductModel._collection(db).count_documents(query)

        return {
            "data": data,
            "metadata": {
                "page": page,
                "limit": limit,
                "total": total,
            },
        }

    @staticmethod
    def find_by_id(db: Database, product_id: int) -> Optional[Dict[str, Any]]:
        doc = ProductModel._collection(db).find_one({"id": product_id}, {"_id": 0})
        return doc

    @staticmethod
    def update(db: Database, product_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        update_data = {
            "name": payload["name"].strip(),
            "description": payload["description"].strip(),
            "price": float(payload["price"]),
            "stock": int(payload["stock"]),
            "category": payload["category"].strip(),
        }

        result = ProductModel._collection(db).update_one(
            {"id": product_id},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            return None

        return ProductModel.find_by_id(db, product_id)

    @staticmethod
    def delete(db: Database, product_id: int) -> bool:
        result = ProductModel._collection(db).delete_one({"id": product_id})
        return result.deleted_count > 0