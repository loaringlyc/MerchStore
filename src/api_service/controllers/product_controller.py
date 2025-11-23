import grpc
import datetime
from db_proto import db_pb2
from google.protobuf.json_format import MessageToDict

from ..clients import clients
from ..logger import log_single_message

def get_product_by_id(product_id: str):
    """
    Input: product id
    Output: Tuple(product dict, info code)
    """
    print(f"Controller: Attempting to fetch product with ID: {product_id}")

    try:
        # send a log
        log_single_message("INFO", f"Attempting to fetch product with ID: {product_id}")

        # get the info from gRPC server
        request = db_pb2.GetProductRequest(id=product_id)
        product_response = clients.db_product.GetProduct(request)
        
        # product_dict = {
        #     "id": product_response.id,
        #     "name": product_response.name,
        #     "description": product_response.description,
        #     "category": product_response.category,
        #     "price": product_response.price,
        #     "slogan": product_response.slogan,
        #     "stock": product_response.stock,
        #     "created_at": product_response.created_at
        # }

        product_dict = MessageToDict(product_response, preserving_proto_field_name=True)

        print(f"Controller: Successfully fetched product: {product_dict['name']}")
        
        # send another log
        log_single_message("INFO", f"Successfully fetched product: {product_response.name}")
        
        return product_dict, 200

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            print(f"Controller: Product with ID {product_id} not found in db_service.")
            # in API, it will return 404
            log_single_message("INFO", f"Not Found Error when fetching product {product_id}: {e.details()}")
            error_message = {"message": f"Product with ID {product_id} not found."}
            return error_message, 404
        
        else:
            print(f"Controller: An RPC error occurred: {e.code()} - {e.details()}")
            log_single_message("ERROR", f"gRPC error while fetching product {product_id}: {e.details()}")
            error_message = {"message": "An error occurred while communicating with a backend service."}
            return error_message, 503
            

def list_products(limit: int = 10, offset: int = 0):
    """
    Input: limit (int), offset (int)
    Output: Tuple(list of product dicts, info code)
    """
    print(f"Controller: Attempting to fetch products with limit={limit}, offset={offset}")

    try:
        log_single_message("INFO", f"Attempting to list products with limit={limit}, offset={offset}")

        request = db_pb2.ListProductsRequest(limit=limit, offset=offset)
        response = clients.db_product.ListProducts(request)

        products_list = [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "stock": p.stock
            }
            for p in response.products
        ]

        print(f"Controller: Successfully fetched {len(products_list)} products.")
        log_single_message("INFO", f"Successfully listed {len(products_list)} products.")

        return products_list, 200

    except grpc.RpcError as e:
        print(f"Controller: An RPC error occurred while listing products: {e.code()} - {e.details()}")
        log_single_message("ERROR", f"gRPC error while listing products: {e.details()}")
        error_message = {"message": "An error occurred while communicating with the backend service."}
        return error_message, 503