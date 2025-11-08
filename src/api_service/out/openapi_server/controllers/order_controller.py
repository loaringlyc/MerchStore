import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.order_info import OrderInfo  # noqa: E501
from openapi_server.models.order_item import OrderItem  # noqa: E501
from openapi_server import util


def cancel_order(order_id):  # noqa: E501
    """Cancel an existing order

     # noqa: E501

    :param order_id: The ID of the order to cancel.
    :type order_id: int

    :rtype: Union[OrderInfo, Tuple[OrderInfo, int], Tuple[OrderInfo, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_order_by_id(order_id):  # noqa: E501
    """Get details of a specific order

     # noqa: E501

    :param order_id: The ID of the order to retrieve.
    :type order_id: int

    :rtype: Union[OrderInfo, Tuple[OrderInfo, int], Tuple[OrderInfo, int, Dict[str, str]]
    """
    return 'do some magic!'


def list_orders(limit=None, offset=None):  # noqa: E501
    """Get all orders for the user

     # noqa: E501

    :param limit: Maximum number of orders to return
    :type limit: int
    :param offset: Number of orders to skip for pagination
    :type offset: int

    :rtype: Union[List[OrderInfo], Tuple[List[OrderInfo], int], Tuple[List[OrderInfo], int, Dict[str, str]]
    """
    return 'do some magic!'


def place_order(body):  # noqa: E501
    """Place a new order

     # noqa: E501

    :param order_item: A list of products and their quantities to order.
    :type order_item: dict | bytes

    :rtype: Union[OrderInfo, Tuple[OrderInfo, int], Tuple[OrderInfo, int, Dict[str, str]]
    """
    order_item = body
    if connexion.request.is_json:
        order_item = OrderItem.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
