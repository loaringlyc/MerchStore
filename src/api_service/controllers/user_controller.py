import grpc
import connexion
import datetime
import jwt
import os
from flask import request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from google.protobuf.json_format import MessageToDict

from db_proto import db_pb2
from src.api_service.out.openapi_server import models

from ..clients import clients
from ..logger import log_single_message

SECRET_KEY = os.getenv('SECRET_KEY', "my_secret_key")

def register_user(body):
    """
    Register a new user.
    Input: user_registration 
    Output: Tuple(user info dict, info code)
    """
    user_registration = body
    if connexion.request.is_json:
        user_registration = models.UserRegistration.from_dict(
            connexion.request.get_json()
        )

    print(f"Controller: Attempting to register a user {user_registration.username}")
    try:
        log_single_message("INFO", f"Attempting to register user: {user_registration.username}")
        
        request = db_pb2.CreateUserRequest(
            sid=user_registration.sid,
            username=user_registration.username,
            email=user_registration.email,
            password_hash=user_registration.password
        )
        response = clients.db_user.CreateUser(request)  
        response_dict = MessageToDict(response, preserving_proto_field_name=True)

        user_info = {
            "id": response_dict.get("id"),
            "sid": response_dict.get("sid"),
            "username": response_dict.get("username"),
            "email": response_dict.get("email"),
            "created_at": response_dict.get("created_at")
        }

        log_single_message("INFO", f"User {user_registration.username} registers successfully.")
        return user_info, 201

    except grpc.RpcError as e:
        log_single_message("ERROR", f"User registration failed: {e}")
        return {"message": f"Registration failed due to database error: {e}"}, 500
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during registration: {e}")
        return {"message": f"Internal server error: {e}"}, 500


def login_user(body):
    """
    Login
    Input: login information
    Output: Tuple(token, info code)
    """
    user_login = body
    if connexion.request.is_json:
        user_login = models.UserLogin.from_dict(
            connexion.request.get_json()
        )

    print(f"Controller: Attempting to login for user {user_login.sid}")
    try:
        log_single_message("INFO", f"Attempting to login for user {user_login.sid}")

        request = db_pb2.LoginUserRequest(
            sid=user_login.sid,
            password_hash=user_login.password
        )
        response = clients.db_user.LoginUser(request)
        if not response.success:
            return {"message": "Invalid credentials"}, 401
        
        user_dict = MessageToDict(response.user, preserving_proto_field_name=True)
        
        payload = {
            "user_id": response.user.id,
            "sid": response.user.sid,
            "username": response.user.username,
            "email": response.user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1 hour
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        log_single_message("INFO", f"Login Successful for user {user_login.sid}")
        return {
            "token": token,
            "user": user_dict
        }, 200
    
    except grpc.RpcError as e:
        log_single_message("ERROR", f"Login failed for user {user_login.sid}: {e}")
        return {"message": "Login failed due to server error"}, 500
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during registration: {e}")
        return {"message": "Internal server error"}, 500
    

def get_current_user():
    """
    Get information for current user
    """
    print(f"Controller: Attempting to get information about current user")
    try:
        log_single_message("INFO", "Attempting to get information about current user")

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid token"}, 401
        
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        user_id = payload["user_id"]
        grpc_request = db_pb2.GetUserRequest(id=user_id)
        grpc_response = clients.db_user.GetUser(grpc_request)

        user_dict = MessageToDict(
            grpc_response, 
            preserving_proto_field_name=True
        )
        return user_dict, 200
    
    except ExpiredSignatureError:
        log_single_message("ERROR", f"Token expired for current user")
        return {"message": "Token has expired"}, 401
    except InvalidTokenError:
        log_single_message("ERROR", f"Token invalid for current user")
        return {"message": "Invalid token"}, 401
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during token validation: {e}")
        return {"message": "Internal server error"}, 500

def update_current_user(body):
    """
    Update current user information
    """
    user_update = body
    if connexion.request.is_json:
        user_update = models.UserUpdate.from_dict(
            connexion.request.get_json()
        )

    print(f"Controller: Attempting to get information about current user")
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid token"}, 401
        
        token = auth_header.split(" ")[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        update_fields = {}
        if user_update.email:
            update_fields["email"] = user_update.email
        if user_update.password:
            update_fields["password"] = user_update.password

        if not update_fields:
            return {"message": "No fields to update"}, 400
        
        grpc_request = db_pb2.UpdateUserRequest(
            id=user_id,
            email=update_fields.get("email"),
            password_hash=update_fields.get("password")
        )
        grpc_response = clients.db_user.UpdateUser(grpc_request)
        
        user_dict = MessageToDict(grpc_response, preserving_proto_field_name=True)
        return user_dict, 200
    
    except ExpiredSignatureError:
        log_single_message("ERROR", f"Failed to update user: toke expired")
        return {"message": "Token has expired"}, 401
    except InvalidTokenError:
        log_single_message("ERROR", f"Failed to update user: token invalid")
        return {"message": "Invalid token"}, 401
    except grpc.RpcError as e:
        log_single_message("ERROR", f"Failed to update user: {e}")
        return {"message": "Failed to update user due to server error"}, 500
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during user update: {e}")
        return {"message": "Internal server error"}, 500
    

def deactivate_user():
    """
    Delete the current user based on the provided JWT token.
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid token"}, 401

        token = auth_header.split(" ")[1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        grpc_request = db_pb2.DeleteUserRequest(id=user_id)
        clients.db_user.DeleteUser(grpc_request)

        return {"message": "User deleted successfully"}, 200

    except ExpiredSignatureError:
        log_single_message("ERROR", f"Failed to delete user: toke expired")
        return {"message": "Token has expired"}, 401
    except InvalidTokenError:
        log_single_message("ERROR", f"Failed to delete user: token invalid")
        return {"message": "Invalid token"}, 401
    except grpc.RpcError as e:
        log_single_message("ERROR", f"Failed to delete user: {e}")
        return {"message": "Failed to delete user due to server error"}, 500
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during user deletion: {e}")
        return {"message": "Internal server error"}, 500
