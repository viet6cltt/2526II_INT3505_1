from flask import jsonify, request

import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.product_create_request import ProductCreateRequest  # noqa: E501
from openapi_server.models.product_detail import ProductDetail  # noqa: E501
from openapi_server.models.product_update_request import ProductUpdateRequest  # noqa: E501
from openapi_server.models.products_get200_response import ProductsGet200Response  # noqa: E501
from openapi_server.models.products_id_delete200_response import ProductsIdDelete200Response  # noqa: E501
from openapi_server import util

from openapi_server.db import db
from openapi_server.models.product import ProductModel


def _error_response(status_code: int, message: str, details: str | None = None):
    body = {
        "error": {
            "code": status_code,
            "message": message,
        }
    }
    if details:
        body["error"]["details"] = details

    return body, status_code


def _normalize_payload(payload):
    if payload is None:
        return None

    if hasattr(payload, "to_dict"):
        return payload.to_dict()

    if isinstance(payload, dict):
        return payload

    return None


def products_get(page=None, limit=None, category=None, search=None):  # noqa: E501
    """List products

    Retrieve a paginated list of products # noqa: E501

    :param page:
    :type page: int
    :param limit:
    :type limit: int
    :param category:
    :type category: str
    :param search:
    :type search: str

    :rtype: Union[ProductsGet200Response, Tuple[ProductsGet200Response, int], Tuple[ProductsGet200Response, int, Dict[str, str]]]
    """
    try:
        page = int(page or request.args.get("page", 1))
        limit = int(limit or request.args.get("limit", 10))
        category = category or request.args.get("category")
        search = search or request.args.get("search")

        if page < 1:
            return _error_response(400, "Bad Request", "Page must be >= 1")

        if limit < 1 or limit > 100:
            return _error_response(400, "Bad Request", "Limit must be between 1 and 100")

        result = ProductModel.find_all(
            db=db,
            page=page,
            limit=limit,
            category=category,
            search=search,
        )

        return result, 200

    except ValueError:
        return _error_response(400, "Bad Request", "Invalid query parameter")
    except Exception as e:
        return _error_response(500, "Internal Server Error", str(e))


def products_id_delete(id):  # noqa: E501
    """Delete product

    Delete a product by id # noqa: E501

    :param id: Product id
    :type id: int

    :rtype: Union[ProductsIdDelete200Response, Tuple[ProductsIdDelete200Response, int], Tuple[ProductsIdDelete200Response, int, Dict[str, str]]]
    """
    try:
        product_id = int(id)

        if product_id < 1:
            return _error_response(400, "Bad Request", "Product id must be >= 1")

        deleted = ProductModel.delete(db=db, product_id=product_id)

        if not deleted:
            return _error_response(404, "Not Found", "Product not found")

        return {
            "message": "Product deleted successfully"
        }, 200

    except ValueError:
        return _error_response(400, "Bad Request", "Product id must be an integer")
    except Exception as e:
        return _error_response(500, "Internal Server Error", str(e))


def products_id_get(id):  # noqa: E501
    """Get product by id

    Retrieve detailed information of a product by id # noqa: E501

    :param id: Product id
    :type id: int

    :rtype: Union[ProductDetail, Tuple[ProductDetail, int], Tuple[ProductDetail, int, Dict[str, str]]]
    """
    try:
        product_id = int(id)

        if product_id < 1:
            return _error_response(400, "Bad Request", "Product id must be >= 1")

        doc = ProductModel.find_by_id(db=db, product_id=product_id)

        if not doc:
            return _error_response(404, "Not Found", "Product not found")

        return ProductModel.to_detail(doc), 200

    except ValueError:
        return _error_response(400, "Bad Request", "Product id must be an integer")
    except Exception as e:
        return _error_response(500, "Internal Server Error", str(e))


def products_id_put(id, body):  # noqa: E501
    """Update product

    Update full info of a product # noqa: E501

    :param id: Product id
    :type id: int
    :param body:
    :type body: dict | bytes

    :rtype: Union[ProductDetail, Tuple[ProductDetail, int], Tuple[ProductDetail, int, Dict[str, str]]]
    """
    try:
        product_id = int(id)

        if product_id < 1:
            return _error_response(400, "Bad Request", "Product id must be >= 1")

        product_update_request = body
        if connexion.request.is_json:
            product_update_request = ProductUpdateRequest.from_dict(
                connexion.request.get_json()
            )

        payload = _normalize_payload(product_update_request)
        if payload is None:
            return _error_response(400, "Bad Request", "Request body must be valid JSON")

        error = ProductModel.validate_payload(payload, partial=False)
        if error:
            return _error_response(400, "Bad Request", error)

        updated = ProductModel.update(
            db=db,
            product_id=product_id,
            payload=payload,
        )

        if not updated:
            return _error_response(404, "Not Found", "Product not found")

        return ProductModel.to_detail(updated), 200

    except ValueError:
        return _error_response(400, "Bad Request", "Product id must be an integer")
    except Exception as e:
        return _error_response(500, "Internal Server Error", str(e))


def products_post(body):  # noqa: E501
    """Create a new product

    Add a new product into the system # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: Union[ProductDetail, Tuple[ProductDetail, int], Tuple[ProductDetail, int, Dict[str, str]]]
    """
    try:
        product_create_request = body
        if connexion.request.is_json:
            product_create_request = ProductCreateRequest.from_dict(
                connexion.request.get_json()
            )

        payload = _normalize_payload(product_create_request)
        if payload is None:
            return _error_response(400, "Bad Request", "Request body must be valid JSON")

        error = ProductModel.validate_payload(payload, partial=False)
        if error:
            return _error_response(400, "Bad Request", error)

        created = ProductModel.create(db=db, payload=payload)

        return ProductModel.to_detail(created), 201

    except Exception as e:
        return _error_response(500, "Internal Server Error", str(e))