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

    :rtype: Union[ProductsGet200Response, Tuple[ProductsGet200Response, int], Tuple[ProductsGet200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def products_id_delete(id):  # noqa: E501
    """Delete product

    Delete a product by id # noqa: E501

    :param id: Product id
    :type id: int

    :rtype: Union[ProductsIdDelete200Response, Tuple[ProductsIdDelete200Response, int], Tuple[ProductsIdDelete200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def products_id_get(id):  # noqa: E501
    """Get product by id

    Retrieve detailed information of a product by id # noqa: E501

    :param id: Product id
    :type id: int

    :rtype: Union[ProductDetail, Tuple[ProductDetail, int], Tuple[ProductDetail, int, Dict[str, str]]
    """
    return 'do some magic!'


def products_id_put(id, body):  # noqa: E501
    """Update product

    Update full info of a product # noqa: E501

    :param id: Product id
    :type id: int
    :param product_update_request: 
    :type product_update_request: dict | bytes

    :rtype: Union[ProductDetail, Tuple[ProductDetail, int], Tuple[ProductDetail, int, Dict[str, str]]
    """
    product_update_request = body
    if connexion.request.is_json:
        product_update_request = ProductUpdateRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def products_post(body):  # noqa: E501
    """Create a new product

    Add a new product into the system # noqa: E501

    :param product_create_request: 
    :type product_create_request: dict | bytes

    :rtype: Union[ProductDetail, Tuple[ProductDetail, int], Tuple[ProductDetail, int, Dict[str, str]]
    """
    product_create_request = body
    if connexion.request.is_json:
        product_create_request = ProductCreateRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
