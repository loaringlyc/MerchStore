from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LogMessage(_message.Message):
    __slots__ = ("level", "timestamp", "message")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    level: str
    timestamp: _timestamp_pb2.Timestamp
    message: str
    def __init__(self, level: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class RecordLogsResponse(_message.Message):
    __slots__ = ("success", "received_count")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_COUNT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    received_count: int
    def __init__(self, success: bool = ..., received_count: _Optional[int] = ...) -> None: ...
