from datetime import datetime
import re
from typing import Dict
from typing import Tuple
from typing import Union

import connexion
from pymongo import ASCENDING
from pymongo.errors import PyMongoError

from openapi_server.database import get_products_collection
from openapi_server.models.api_error import ApiError
from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.product import Product
from openapi_server.models.product_base import ProductBase
from openapi_server.models.product_list_item import ProductListItem
from openapi_server.models.product_list_item_metadata import ProductListItemMetadata
from openapi_server.models.products_id_delete200_response import ProductsIdDelete200Response


def _utcnow() -> datetime:
    return datetime.utcnow()


def _error_response(status_code: int, message: str, details: str = None):
    return (
        ErrorResponse(
            error=ApiError(
                code=status_code,
                message=message,
                details=details,
            )
        ),
        status_code,
    )


def _server_error_response(details: str):
    return _error_response(500, "Internal Server Error", details)


def _coerce_product_body(body) -> Union[ProductBase, Tuple[ErrorResponse, int]]:
    payload = body
    if payload is None and connexion.request.is_json:
        payload = connexion.request.get_json()

    if isinstance(payload, ProductBase):
        return payload

    if not isinstance(payload, dict):
        return _error_response(400, "Bad Request", "Request body must be a JSON object")

    try:
        return ProductBase.from_dict(payload)
    except (TypeError, ValueError) as exc:
        return _error_response(400, "Bad Request", str(exc))


def _validate_product_payload(product_base: ProductBase):
    required_fields = {
        "name": product_base.name,
        "description": product_base.description,
        "price": product_base.price,
        "category": product_base.category,
    }

    for field_name, value in required_fields.items():
        if value is None:
            return _error_response(400, "Bad Request", f"`{field_name}` is required")

    if product_base.price is not None and product_base.price < 0:
        return _error_response(400, "Bad Request", "`price` must be greater than or equal to 0")

    if product_base.stock is not None and product_base.stock < 0:
        return _error_response(400, "Bad Request", "`stock` must be greater than or equal to 0")

    return None


def _build_product(product_id: str, product_base: ProductBase, created_at: datetime) -> Product:
    return Product(
        id=product_id,
        name=product_base.name,
        description=product_base.description,
        price=float(product_base.price),
        stock=product_base.stock if product_base.stock is not None else 0,
        category=product_base.category,
        created_at=created_at,
        updated_at=_utcnow(),
    )


def _product_to_document(product: Product) -> Dict[str, object]:
    return {
        "_id": product.id,
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "category": product.category,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


def _document_to_product(document: Dict[str, object]) -> Product:
    created_at = document.get("created_at") or document.get("createdAt") or _utcnow()
    updated_at = document.get("updated_at") or document.get("updatedAt") or created_at

    return Product(
        id=str(document.get("id", document.get("_id", ""))),
        name=document["name"],
        description=document["description"],
        price=float(document["price"]),
        stock=int(document.get("stock", 0)),
        category=document["category"],
        created_at=created_at,
        updated_at=updated_at,
    )


def _get_collection():
    return get_products_collection()


def _get_product_or_404(product_id: int):
    try:
        document = _get_collection().find_one({"id": str(product_id)})
    except PyMongoError as exc:
        return _server_error_response(str(exc))

    if document is None:
        return _error_response(404, "Not Found", f"Product with id `{product_id}` was not found")

    return _document_to_product(document)


def _get_next_product_id() -> str:
    numeric_ids = [
        int(item["id"])
        for item in _get_collection().find(
            {"id": {"$regex": r"^\d+$"}},
            projection={"id": 1},
        )
        if str(item.get("id", "")).isdigit()
    ]
    return str(max(numeric_ids, default=0) + 1)


def products_get(page=None, limit=None, category=None, search=None):  # noqa: E501
    """Get list of products

    Retrieve a paginated list of products with optional filtering # noqa: E501

    :param page: Page number starting from 1
    :type page: int
    :param limit: Number of items per page
    :type limit: int
    :param category: Filter products by category
    :type category: str
    :param search: Search products by name
    :type search: str

    :rtype: Union[ProductListItem, Tuple[ProductListItem, int], Tuple[ProductListItem, int, Dict[str, str]]
    """
    page = page or 1
    limit = limit or 10

    if page < 1:
        return _error_response(400, "Bad Request", "`page` must be greater than or equal to 1")

    if limit < 1 or limit > 20:
        return _error_response(400, "Bad Request", "`limit` must be between 1 and 20")

    query = {}
    if category:
        query["category"] = {"$regex": f"^{re.escape(category)}$", "$options": "i"}
    if search:
        query["name"] = {"$regex": re.escape(search), "$options": "i"}

    try:
        collection = _get_collection()
        total = collection.count_documents(query)
        cursor = (
            collection.find(query)
            .sort("id", ASCENDING)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        products = [_document_to_product(document) for document in cursor]
    except PyMongoError as exc:
        return _server_error_response(str(exc))

    return ProductListItem(
        data=products,
        metadata=ProductListItemMetadata(page=page, limit=limit, total=total),
    )


def products_id_delete(id):  # noqa: E501
    """Delete product

    Delete a product by id # noqa: E501

    :param id: Product id
    :type id: int

    :rtype: Union[ProductsIdDelete200Response, Tuple[ProductsIdDelete200Response, int], Tuple[ProductsIdDelete200Response, int, Dict[str, str]]
    """
    try:
        result = _get_collection().delete_one({"id": str(id)})
    except PyMongoError as exc:
        return _server_error_response(str(exc))

    if result.deleted_count == 0:
        return _error_response(404, "Not Found", f"Product with id `{id}` was not found")

    return ProductsIdDelete200Response(message="Product deleted successfully")


def products_id_get(id):  # noqa: E501
    """Get product by id

    Retrieve detailed information of a product by id # noqa: E501

    :param id: Product id
    :type id: int

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    return _get_product_or_404(id)


def products_id_put(id, body):  # noqa: E501
    """Update product

    Update full info of a product # noqa: E501

    :param id: Product id
    :type id: int
    :param body:
    :type body:

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    existing_product = _get_product_or_404(id)
    if isinstance(existing_product, tuple):
        return existing_product

    product_base = _coerce_product_body(body)
    if isinstance(product_base, tuple):
        return product_base

    validation_error = _validate_product_payload(product_base)
    if validation_error:
        return validation_error

    updated_product = _build_product(str(id), product_base, existing_product.created_at)

    try:
        _get_collection().replace_one(
            {"id": str(id)},
            _product_to_document(updated_product),
        )
    except PyMongoError as exc:
        return _server_error_response(str(exc))

    return updated_product


def products_post(body):  # noqa: E501
    """Create a new product

    Add a new product into the system # noqa: E501

    :param body:
    :type body:

    :rtype: Union[Product, Tuple[Product, int], Tuple[Product, int, Dict[str, str]]
    """
    product_base = _coerce_product_body(body)
    if isinstance(product_base, tuple):
        return product_base

    validation_error = _validate_product_payload(product_base)
    if validation_error:
        return validation_error

    try:
        product_id = _get_next_product_id()
        created_at = _utcnow()
        product = _build_product(product_id, product_base, created_at)
        _get_collection().insert_one(_product_to_document(product))
    except PyMongoError as exc:
        return _server_error_response(str(exc))

    return product, 201
