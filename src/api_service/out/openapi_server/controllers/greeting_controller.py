import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.message import Message  # noqa: E501
from openapi_server import util


def greet():  # noqa: E501
    """greet

    Get a hello-world greeting. # noqa: E501


    :rtype: Union[Message, Tuple[Message, int], Tuple[Message, int, Dict[str, str]]
    """
    return 'do some magic!'
