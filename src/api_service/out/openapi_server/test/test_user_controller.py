import unittest

from flask import json

from openapi_server.models.auth_token import AuthToken  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.user_info import UserInfo  # noqa: E501
from openapi_server.models.user_login import UserLogin  # noqa: E501
from openapi_server.models.user_registration import UserRegistration  # noqa: E501
from openapi_server.models.user_update import UserUpdate  # noqa: E501
from openapi_server.test import BaseTestCase


class TestUserController(BaseTestCase):
    """UserController integration test stubs"""

    def test_get_current_user(self):
        """Test case for get_current_user

        Get current user's profile
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/users/me',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_login_user(self):
        """Test case for login_user

        Logs user into the system
        """
        user_login = {"password":"password","sid":"sid"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/users/login',
            method='POST',
            headers=headers,
            data=json.dumps(user_login),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_register_user(self):
        """Test case for register_user

        Register a new user
        """
        user_registration = {"password":"password","email":"12211418@mail.sustech.edu.cn","sid":"12211418","username":"loring"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/users/register',
            method='POST',
            headers=headers,
            data=json.dumps(user_registration),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_current_user(self):
        """Test case for update_current_user

        Update current user's profile
        """
        user_update = {"password":"a-very-strong-new-password","email":"new.email@example.com"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/users/me',
            method='PUT',
            headers=headers,
            data=json.dumps(user_update),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
