import unittest

from flask import json

from openapi_server.models.book_create_request import BookCreateRequest  # noqa: E501
from openapi_server.models.book_update_request import BookUpdateRequest  # noqa: E501
from openapi_server.models.books_get200_response import BooksGet200Response  # noqa: E501
from openapi_server.models.books_post201_response import BooksPost201Response  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_books_book_id_delete(self):
        """Test case for books_book_id_delete

        Delete a book
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/books/{book_id}'.format(book_id=56),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_book_id_get(self):
        """Test case for books_book_id_get

        Get book detail by id
        """
        headers = { 
            'Accept': 'application/json',
            'cache_control': 'no-cache',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/books/{book_id}'.format(book_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_book_id_put(self):
        """Test case for books_book_id_put

        Update
        """
        book_update_request = {"author":"Robert C. Martin","title":"Clean Code","category":"IT"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/books/{book_id}'.format(book_id=56),
            method='PUT',
            headers=headers,
            data=json.dumps(book_update_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_get(self):
        """Test case for books_get

        Get list of books
        """
        query_string = [('page', 1),
                        ('limit', 10),
                        ('category', 'IT')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/books',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_books_post(self):
        """Test case for books_post

        Create a new book
        """
        book_create_request = {"author":"Robert C. Martin","title":"Clean Code","category":"IT"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/books',
            method='POST',
            headers=headers,
            data=json.dumps(book_create_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
