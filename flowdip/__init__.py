from enum import IntEnum
import logging
from dataclasses import dataclass
from typing import Any

# =============================================================================
#  Enums and data structures
# =============================================================================

class RequestType(IntEnum):
    SHUTDOWN = -1
    CREATE_NODE = 0
    EDIT_NODE = 1
    DELETE_NODE = 2
    RUN_NODE = 3

class EventType(IntEnum):
    SHUTDOWN = -1
    UPDATE_NODE_STATE = 0
    UPDATE_PORT_STATE = 1
    SEND_FRAME = 2

@dataclass
class Request:
    request_type: RequestType
    payload: Any

@dataclass
class Event:
    event_type: EventType
    payload: Any

@dataclass
class CreateNodePayload:
    node_class_name: str
    flowdip_name: str
    loop: bool = False
    other_params: dict = None

@dataclass
class DeleteNodePayload:
    node_class_name: str
    flowdip_name: str

# =============================================================================
# Helper: logger factory
# =============================================================================
def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name, configured if not already."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger