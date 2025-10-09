from enum import IntEnum
from dataclasses import dataclass
from typing import Any

# =============================================================================
#  Enums and data structures
# =============================================================================

class RequestType(IntEnum):
    CREATE_NODE = 0
    EDIT_NODE = 1
    RUN_NODE = 2
    SHUTDOWN = 3

class EventType(IntEnum):
    UPDATE_NODE_STATE = 0
    UPDATE_PORT_STATE = 1
    SEND_FRAME = 2
    SHUTDOWN = 3

@dataclass
class Request:
    request_type: RequestType
    payload: Any

@dataclass
class Event:
    event_type: EventType
    payload: Any