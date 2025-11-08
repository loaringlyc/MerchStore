import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.product_breif_info import ProductBreifInfo  # noqa: E501
from openapi_server.models.product_info import ProductInfo  # noqa: E501
from openapi_server.test import BaseTestCase


class TestProductController(BaseTestCase):
    """ProductController integration test stubs"""

    def test_get_product_by_id(self):
        """Test case for get_product_by_id

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/products/{product_id}'.format(product_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_products(self):
        """Test case for list_products

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/products',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
