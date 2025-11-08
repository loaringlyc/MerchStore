import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.auth_token import AuthToken  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.user_info import UserInfo  # noqa: E501
from openapi_server.models.user_login import UserLogin  # noqa: E501
from openapi_server.models.user_registration import UserRegistration  # noqa: E501
from openapi_server.models.user_update import UserUpdate  # noqa: E501
from openapi_server import util


def get_current_user():  # noqa: E501
    """Get current user&#39;s profile

     # noqa: E501


    :rtype: Union[UserInfo, Tuple[UserInfo, int], Tuple[UserInfo, int, Dict[str, str]]
    """
    return 'do some magic!'


def login_user(body):  # noqa: E501
    """Logs user into the system

     # noqa: E501

    :param user_login: 
    :type user_login: dict | bytes

    :rtype: Union[AuthToken, Tuple[AuthToken, int], Tuple[AuthToken, int, Dict[str, str]]
    """
    user_login = body
    if connexion.request.is_json:
        user_login = UserLogin.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def register_user(body):  # noqa: E501
    """Register a new user

     # noqa: E501

    :param user_registration: 
    :type user_registration: dict | bytes

    :rtype: Union[UserInfo, Tuple[UserInfo, int], Tuple[UserInfo, int, Dict[str, str]]
    """
    user_registration = body
    if connexion.request.is_json:
        user_registration = UserRegistration.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def update_current_user(body):  # noqa: E501
    """Update current user&#39;s profile

     # noqa: E501

    :param user_update: Fields to update for the user. Only non-null fields will be updated.
    :type user_update: dict | bytes

    :rtype: Union[UserInfo, Tuple[UserInfo, int], Tuple[UserInfo, int, Dict[str, str]]
    """
    user_update = body
    if connexion.request.is_json:
        user_update = UserUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
