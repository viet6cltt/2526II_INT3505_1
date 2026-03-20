import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.book_create_request import BookCreateRequest  # noqa: E501
from openapi_server.models.book_update_request import BookUpdateRequest  # noqa: E501
from openapi_server.models.books_get200_response import BooksGet200Response  # noqa: E501
from openapi_server.models.books_post201_response import BooksPost201Response  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server import util


def books_book_id_delete(book_id):  # noqa: E501
    """Delete a book

    Remove a book by ID # noqa: E501

    :param book_id: ID of the book
    :type book_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def books_book_id_get(book_id, cache_control=None):  # noqa: E501
    """Get book detail by id

    Return book detail by book id # noqa: E501

    :param book_id: ID of the book
    :type book_id: int
    :param cache_control: Control cache of response
    :type cache_control: str

    :rtype: Union[BooksPost201Response, Tuple[BooksPost201Response, int], Tuple[BooksPost201Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def books_book_id_put(book_id, body):  # noqa: E501
    """Update

    Update full info of a book # noqa: E501

    :param book_id: ID of the book
    :type book_id: int
    :param book_update_request: 
    :type book_update_request: dict | bytes

    :rtype: Union[BooksPost201Response, Tuple[BooksPost201Response, int], Tuple[BooksPost201Response, int, Dict[str, str]]
    """
    book_update_request = body
    if connexion.request.is_json:
        book_update_request = BookUpdateRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def books_get(page=None, limit=None, category=None):  # noqa: E501
    """Get list of books

    Retrieve a paginated list of books with optional filtering # noqa: E501

    :param page: Page number starting from 1
    :type page: int
    :param limit: Number of items per page
    :type limit: int
    :param category: Filter books by category
    :type category: str

    :rtype: Union[BooksGet200Response, Tuple[BooksGet200Response, int], Tuple[BooksGet200Response, int, Dict[str, str]]
    """
    return 'do some magic!'


def books_post(body):  # noqa: E501
    """Create a new book

    Create a new book # noqa: E501

    :param book_create_request: 
    :type book_create_request: dict | bytes

    :rtype: Union[BooksPost201Response, Tuple[BooksPost201Response, int], Tuple[BooksPost201Response, int, Dict[str, str]]
    """
    book_create_request = body
    if connexion.request.is_json:
        book_create_request = BookCreateRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
