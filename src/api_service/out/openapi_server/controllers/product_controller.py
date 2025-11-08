import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.product_breif_info import ProductBreifInfo  # noqa: E501
from openapi_server.models.product_info import ProductInfo  # noqa: E501
from openapi_server import util


def get_product_by_id(product_id):  # noqa: E501
    """get_product_by_id

    Find product by ID # noqa: E501

    :param product_id: The ID of the product to get
    :type product_id: int

    :rtype: Union[ProductInfo, Tuple[ProductInfo, int], Tuple[ProductInfo, int, Dict[str, str]]
    """
    return 'do some magic!'


def list_products():  # noqa: E501
    """list_products

    Get all products on sale # noqa: E501


    :rtype: Union[List[ProductBreifInfo], Tuple[List[ProductBreifInfo], int], Tuple[List[ProductBreifInfo], int, Dict[str, str]]
    """
    return 'do some magic!'
