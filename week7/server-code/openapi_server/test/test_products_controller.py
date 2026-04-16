import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.product_create_request import ProductCreateRequest  # noqa: E501
from openapi_server.models.product_detail import ProductDetail  # noqa: E501
from openapi_server.models.product_update_request import ProductUpdateRequest  # noqa: E501
from openapi_server.models.products_get200_response import ProductsGet200Response  # noqa: E501
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
        product_update_request = {"price":1099.99,"name":"iPhone 15 Pro","description":"Updated product description","stock":30,"category":"Electronics"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/products/{id}'.format(id=1),
            method='PUT',
            headers=headers,
            data=json.dumps(product_update_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_products_post(self):
        """Test case for products_post

        Create a new product
        """
        product_create_request = {"price":999.99,"name":"iPhone 15","description":"Latest Apple smartphone with advanced camera system","stock":50,"category":"Electronics"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/products',
            method='POST',
            headers=headers,
            data=json.dumps(product_create_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
