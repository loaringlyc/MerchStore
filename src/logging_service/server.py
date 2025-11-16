import grpc
import json
from concurrent import futures
from confluent_kafka import Producer
from google.protobuf.json_format import MessageToDict

from log_proto import log_pb2
from log_proto import log_pb2_grpc

class LoggingServiceServicer(log_pb2_grpc.LoggingServiceServicer):
    def __init__(self):
        # initialize Kafka producer
        self.producer = Producer({'bootstrap.servers': 'localhost:9093'})
        self.topic = 'log-channel'
        print("Kafka Producer initialized.")

    def RecordLogs(self, request_iterator, context):
        print("Client connected for logging...")
        received_count = 0
        
        try:
            for log_message in request_iterator:
                received_count += 1
                
                log_dict = MessageToDict(log_message)
                log_json = json.dumps(log_dict) # change to JSON string
                self.producer.produce(self.topic, log_json.encode('utf-8')) 
                print(f"Received and published to Kafka: {log_json}")

            self.producer.flush()

        except Exception as e:
            print(f"An error occurred: {e}")
            return log_pb2.RecordLogsResponse(success=False, received_count=0)
        finally:
            self.producer.flush()
            print(f"Client disconnected. Total logs received: {received_count}")

        # when closing stream, return the response
        return log_pb2.RecordLogsResponse(success=True, received_count=received_count)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    log_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingServiceServicer(), server)
    
    port = '50052' 
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Logging Service started, listening on port {port}...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()