import unittest

from flask import json

from openapi_server.models.auth_refresh_post200_response import AuthRefreshPost200Response  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAuthController(BaseTestCase):
    """AuthController integration test stubs"""

    def test_auth_refresh_post(self):
        """Test case for auth_refresh_post

        Refresh access token
        """
        headers = { 
            'Accept': 'application/json',
            'cookieAuth': 'special-key',
        }
        response = self.client.open(
            '/auth/refresh',
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
