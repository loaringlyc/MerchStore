import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.order_info import OrderInfo  # noqa: E501
from openapi_server.models.order_item import OrderItem  # noqa: E501
from openapi_server.test import BaseTestCase


class TestOrderController(BaseTestCase):
    """OrderController integration test stubs"""

    def test_cancel_order(self):
        """Test case for cancel_order

        Cancel an existing order
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/orders/{order_id}/cancel'.format(order_id=56),
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_order_by_id(self):
        """Test case for get_order_by_id

        Get details of a specific order
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/orders/{order_id}'.format(order_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_orders(self):
        """Test case for list_orders

        Get all orders for the user
        """
        query_string = [('limit', 20),
                        ('offset', 0)]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/orders',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_place_order(self):
        """Test case for place_order

        Place a new order
        """
        order_item = {"quantity":2,"product_id":1}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/orders',
            method='POST',
            headers=headers,
            data=json.dumps(order_item),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
