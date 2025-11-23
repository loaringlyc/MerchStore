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


def list_orders(limit: int = 20, offset: int = 0):
    """
    Get all orders for the current user.
    """
    print(f"Controller: Attempting to list orders with limit={limit}, offset={offset}")
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid token"}, 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        log_single_message("INFO", f"Attempting to list orders for user with id {user_id}")

        grpc_request = db_pb2.ListOrdersByUserRequest(user_id=user_id, limit=limit, offset=offset)
        grpc_response = clients.db_order.ListOrdersByUser(grpc_request)

        orders = MessageToDict(grpc_response, preserving_proto_field_name=True).get("orders", [])

        log_single_message("INFO", f"Successfully list orders for user with id {user_id}")
        return orders, 200

    except ExpiredSignatureError:
        log_single_message("ERROR", "Token expired for listing orders")
        return {"message": "Token has expired"}, 401
    except InvalidTokenError:
        log_single_message("ERROR", "Token invalid for listing orders")
        return {"message": "Invalid token"}, 401
    except grpc.RpcError as e:
        log_single_message("ERROR", f"Failed to list orders: {e}")
        return {"message": "Failed to list orders due to server error"}, 500
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during listing orders: {e}")
        return {"message": "Internal server error"}, 500


def place_order(body):
    """
    Place a new order.
    """
    order_request = body
    if connexion.request.is_json:
        order_request = models.OrderItem.from_dict(connexion.request.get_json())

    print(f"Controller: Attempting to place an order for product_id={order_request.product_id}")
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid token"}, 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        log_single_message("INFO", f"Attempting to place an order for product_id={order_request.product_id}, user id {user_id}")

        grpc_product_request = db_pb2.GetProductRequest(id=order_request.product_id)
        grpc_product_response = clients.db_product.GetProduct(grpc_product_request)
        price = grpc_product_response.price

        grpc_request = db_pb2.CreateOrderRequest(
            user_id=user_id,
            product_id=order_request.product_id,
            quantity=order_request.quantity,
            total_price=order_request.quantity * price
        )
        grpc_response = clients.db_order.CreateOrder(grpc_request)

        order_info = MessageToDict(grpc_response, preserving_proto_field_name=True)

        log_single_message("INFO", f"Success to place an order for product_id={order_request.product_id}, user id {user_id}")
        return order_info, 201

    except ExpiredSignatureError:
        log_single_message("ERROR", "Token expired for placing order")
        return {"message": "Token has expired"}, 401
    except InvalidTokenError:
        log_single_message("ERROR", "Token invalid for placing order")
        return {"message": "Invalid token"}, 401
    except grpc.RpcError as e:
        log_single_message("ERROR", f"Failed to place order: {e}")
        return {"message": "Failed to place order due to server error"}, 500
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during placing order: {e}")
        return {"message": "Internal server error"}, 500


def get_order_by_id(order_id: int):
    """
    Get details of a specific order.
    """
    print(f"Controller: Attempting to get order with ID: {order_id}")
    try:
        log_single_message("INFO", f"Attempting to get information for order with order_id={order_id}")
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid token"}, 401

        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload["user_id"]

        grpc_request = db_pb2.GetOrderRequest(id=order_id)
        grpc_response = clients.db_order.GetOrder(grpc_request)

        order_info = MessageToDict(grpc_response, preserving_proto_field_name=True)

        log_single_message("INFO", f"Success to get details for order with id {order_id}")
        return order_info, 200

    except ExpiredSignatureError:
        log_single_message("ERROR", "Token expired for getting order")
        return {"message": "Token has expired"}, 401
    except InvalidTokenError:
        log_single_message("ERROR", "Token invalid for getting order")
        return {"message": "Invalid token"}, 401
    except grpc.RpcError as e:
        log_single_message("ERROR", f"Failed to get order: {e}")
        return {"message": "Failed to get order due to server error"}, 500
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during getting order: {e}")
        return {"message": "Internal server error"}, 500


def cancel_order(order_id: int):
    """
    Cancel an existing order.
    """
    print(f"Controller: Attempting to cancel order with ID: {order_id}")
    try:
        log_single_message("INFO", f"Attempting to cancel an order with order_id={order_id}")
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid token"}, 401

        grpc_request = db_pb2.DeleteOrderRequest(id=order_id)
        grpc_response = clients.db_order.DeleteOrder(grpc_request)

        order_info = MessageToDict(grpc_response, preserving_proto_field_name=True)
        log_single_message("INFO", f"Success to cancel an order with order_id={order_id}")
        return order_info, 200

    except ExpiredSignatureError:
        log_single_message("ERROR", "Token expired for canceling order")
        return {"message": "Token has expired"}, 401
    except InvalidTokenError:
        log_single_message("ERROR", "Token invalid for canceling order")
        return {"message": "Invalid token"}, 401
    except grpc.RpcError as e:
        log_single_message("ERROR", f"Failed to cancel order: {e}")
        return {"message": "Failed to cancel order due to server error"}, 500
    except Exception as e:
        log_single_message("ERROR", f"Unexpected error during canceling order: {e}")
        return {"message": "Internal server error"}, 500