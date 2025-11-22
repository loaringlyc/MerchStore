import grpc
import os 
from db_proto import db_pb2_grpc
from log_proto import log_pb2_grpc

DB_SERVICE_ADDR = os.getenv('DB_SERVICE_ADDR', 'localhost:50051')
LOGGING_SERVICE_ADDR = os.getenv('LOGGING_SERVICE_ADDR', 'localhost:50052')

class Clients:
    def __init__(self):
        # create channel to service
        db_channel = grpc.insecure_channel(DB_SERVICE_ADDR)
        log_channel = grpc.insecure_channel(LOGGING_SERVICE_ADDR)
        
        # create gRPC client-side stubs 
        self.db_product = db_pb2_grpc.ProductServiceStub(db_channel)
        self.db_user = db_pb2_grpc.UserServiceStub(db_channel)
        self.db_order = db_pb2_grpc.OrderServiceStub(db_channel)
        self.log = log_pb2_grpc.LoggingServiceStub(log_channel)
        
        print("gRPC clients for DB and Logging services initialized.")

# global instance
clients = Clients()