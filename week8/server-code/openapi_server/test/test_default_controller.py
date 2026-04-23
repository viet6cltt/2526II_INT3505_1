import unittest

from flask import json

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.book_input import BookInput  # noqa: E501
from openapi_server.models.delete_response import DeleteResponse  # noqa: E501
from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    # """DefaultController integration test stubs"""

    # def test_books_get(self):
    #     """Test case for books_get

    #     Get all books
    #     """
    #     headers = { 
    #         'Accept': 'application/json',
    #     }
    #     response = self.client.open(
    #         '/api/v1/books',
    #         method='GET',
    #         headers=headers)
    #     self.assert200(response,
    #                    'Response body is : ' + response.data.decode('utf-8'))

    # def test_books_id_delete(self):
    #     """Test case for books_id_delete

    #     Delete book
    #     """
    #     headers = { 
    #         'Accept': 'application/json',
    #     }
    #     response = self.client.open(
    #         '/api/v1/books/{id}'.format(id='id_example'),
    #         method='DELETE',
    #         headers=headers)
    #     self.assert200(response,
    #                    'Response body is : ' + response.data.decode('utf-8'))

    # def test_books_id_get(self):
    #     """Test case for books_id_get

    #     Get book by id
    #     """
    #     headers = { 
    #         'Accept': 'application/json',
    #     }
    #     response = self.client.open(
    #         '/api/v1/books/{id}'.format(id='id_example'),
    #         method='GET',
    #         headers=headers)
    #     self.assert200(response,
    #                    'Response body is : ' + response.data.decode('utf-8'))

    # def test_books_id_put(self):
    #     """Test case for books_id_put

    #     Update book
    #     """
    #     book_input = {"author":"Robert C. Martin","price":29.99,"publishedYear":2008,"title":"Clean Code"}
    #     headers = { 
    #         'Accept': 'application/json',
    #         'Content-Type': 'application/json',
    #     }
    #     response = self.client.open(
    #         '/api/v1/books/{id}'.format(id='id_example'),
    #         method='PUT',
    #         headers=headers,
    #         data=json.dumps(book_input),
    #         content_type='application/json')
    #     self.assert200(response,
    #                    'Response body is : ' + response.data.decode('utf-8'))

    # def test_books_post(self):
    #     """Test case for books_post

    #     Create book
    #     """
    #     book_input = {"author":"Robert C. Martin","price":29.99,"publishedYear":2008,"title":"Clean Code"}
    #     headers = { 
    #         'Accept': 'application/json',
    #         'Content-Type': 'application/json',
    #     }
    #     response = self.client.open(
    #         '/api/v1/books',
    #         method='POST',
    #         headers=headers,
    #         data=json.dumps(book_input),
    #         content_type='application/json')
    #     self.assert200(response,
    #                    'Response body is : ' + response.data.decode('utf-8'))

    def test_full_book_flow(self):
        # create
        book_input = {
            "author": "Robert C. Martin",
            "price": 29.99,
            "publishedYear": 2008,
            "title": "Clean Code"
        }

        res = self.client.open(
            '/api/v1/books',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(book_input)
        )
        self.assertStatus(res, 201)

        data = json.loads(res.data.decode())
        book_id = data["id"]

        # get
        res = self.client.open(f'/api/v1/books/{book_id}', method='GET')
        self.assert200(res)

        # update
        res = self.client.open(
            f'/api/v1/books/{book_id}',
            method='PUT',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(book_input)
        )
        self.assert200(res)

        # delete
        res = self.client.open(f'/api/v1/books/{book_id}', method='DELETE')
        self.assert200(res)
        
import unittest

def calculate_discounted_price(price: float, discount_percent: float) -> float:
    if price < 0:
        raise ValueError("price must be >= 0")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")

    final_price = price * (1 - discount_percent / 100)
    return round(final_price, 2)


class TestCalculateDiscountedPrice(unittest.TestCase):
    def test_normal_case(self):
        self.assertEqual(calculate_discounted_price(100, 20), 80.00)

    def test_zero_discount(self):
        self.assertEqual(calculate_discounted_price(100, 0), 100.00)

    def test_full_discount(self):
        self.assertEqual(calculate_discounted_price(100, 100), 0.00)

    def test_rounds_to_two_decimals(self):
        self.assertEqual(calculate_discounted_price(99.99, 12.5), 87.49)

    def test_invalid_price(self):
        with self.assertRaises(ValueError) as context:
            calculate_discounted_price(-10, 20)
        self.assertEqual(str(context.exception), "price must be >= 0")

    def test_invalid_discount_above_100(self):
        with self.assertRaises(ValueError) as context:
            calculate_discounted_price(100, 120)
        self.assertEqual(
            str(context.exception),
            "discount_percent must be between 0 and 100"
        )

    def test_invalid_discount_below_0(self):
        with self.assertRaises(ValueError) as context:
            calculate_discounted_price(100, -5)
        self.assertEqual(
            str(context.exception),
            "discount_percent must be between 0 and 100"
        )

if __name__ == '__main__':
    unittest.main()
