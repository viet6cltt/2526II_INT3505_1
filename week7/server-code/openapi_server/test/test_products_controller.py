import unittest

from flask import json

from openapi_server.models.error_response import ErrorResponse  # noqa: E501
from openapi_server.models.product import Product  # noqa: E501
from openapi_server.models.product_base import ProductBase  # noqa: E501
from openapi_server.models.product_list_item import ProductListItem  # noqa: E501
from openapi_server.models.products_id_delete200_response import ProductsIdDelete200Response  # noqa: E501
from openapi_server.test import BaseTestCase


class TestProductsController(BaseTestCase):
    """ProductsController integration test stubs"""

    def test_products_get(self):
        """Test case for products_get

        Get list of products
        """
        query_string = [('page', 1),
                        ('limit', 10),
                        ('category', 'Electronics'),
                        ('search', 'iPhone')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/products',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_id_delete(self):
        """Test case for products_id_delete

        Delete product
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/products/{id}'.format(id=1),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_id_get(self):
        """Test case for products_id_get

        Get product by id
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/products/{id}'.format(id=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_id_put(self):
        """Test case for products_id_put

        Update product
        """
        body = {"price":999.99,"name":"iPhone 20","description":"The latest iPhone with amazing features.","stock":100,"category":"Electronics"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/products/{id}'.format(id=1),
            method='PUT',
            headers=headers,
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_post(self):
        """Test case for products_post

        Create a new product
        """
        body = {"price":999.99,"name":"iPhone 20","description":"The latest iPhone with amazing features.","stock":100,"category":"Electronics"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/products',
            method='POST',
            headers=headers,
            data=json.dumps(body),
            content_type='application/json')
        self.assertStatus(response, 201,
                          'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
