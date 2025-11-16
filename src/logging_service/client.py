import grpc
import time
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from log_proto import log_pb2
from log_proto import log_pb2_grpc

def generate_log_messages():
    """
    Keeps generating LogMessage objects
    """
    while True:
        ts = Timestamp()
        ts.FromDatetime(datetime.now())
        
        log = log_pb2.LogMessage(
            level="INFO",
            timestamp=ts,
            message=f"API Service health check at {datetime.now()}"
        )
        
        print(f"Sending log: {log.message}")
        yield log
        time.sleep(2) # every two seconds

def run():
    """
    link to Logging Service and send logging information
    """
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = log_pb2_grpc.LoggingServiceStub(channel)
        
        print("--- Starting to stream logs to Logging Service ---")
        
        try:
            # call RecordLogs, pass a generator
            # return future immediately, the streaming is running behind the stage
            response_future = stub.RecordLogs(generate_log_messages())
            
            # interrupt with KeyboardInterrupt 
            response_future.result()

        except KeyboardInterrupt:
            print("\nStopping log stream by keyboard interrupt.")
            response_future.cancel() # cancel 
            print("Log stream cancelled.")
        except grpc.RpcError as e:
            print(f"An RPC error occurred: {e.code()} - {e.details()}")
        
        print("--- Client finished ---")

if __name__ == '__main__':
    run()