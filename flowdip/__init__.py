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
    UPDATE_NODE_PARAMS = 4

class EventType(IntEnum):
    SHUTDOWN = -1
    UPDATE_NODE_STATE = 0
    UPDATE_PORT_STATE = 1
    NEW_FRAME = 2
    UPDATE_NODE_PARAMS = 3

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
    flowdip_name: str

# @dataclass
# class UpdateShmPayload:
#     flowdip_name: str
#     shm_name: str
#     shm_shape: tuple
#     shm_dtype: Any

@dataclass
class UpdateNodeParamsPayload:
    flowdip_name: str
    new_params: dict

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