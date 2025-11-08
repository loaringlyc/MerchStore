import unittest

from flask import json

from openapi_server.models.message import Message  # noqa: E501
from openapi_server.test import BaseTestCase


class TestGreetingController(BaseTestCase):
    """GreetingController integration test stubs"""

    def test_greet(self):
        """Test case for greet

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
