import unittest

from flask import json

from openapi_server.test import BaseTestCase


class TestUsersController(BaseTestCase):
    """UsersController integration test stubs"""

    def test_users_get(self):
        """Test case for users_get

        Get users with debug mode
        """
        headers = { 
        }
        response = self.client.open(
            '/users',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
