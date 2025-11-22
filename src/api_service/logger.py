import time
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from .clients import clients
from log_proto import log_pb2

def log_single_message(level: str, message: str):
    """
    Send single log to Logging Service。
    """
    def message_generator():
        # create Timestamp object
        ts = Timestamp()
        ts.FromDatetime(datetime.now())
        
        # create LogMessage object
        log = log_pb2.LogMessage(
            service_name="api_service",
            level=level,
            timestamp=ts,
            message=message
        )
        # yield makes the function become a generator
        yield log

    try:
        # Call RecordLogs, pass a generator object
        # We do not care the output
        clients.log.RecordLogs(message_generator())
        print(f"Logger: Sent log to logging_service: '{message}'")
    except Exception as e:
        print(f"Logger: Failed to send log. Error: {e}")
