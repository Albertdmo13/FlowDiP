from typing import List, Optional, Any
from enum import IntEnum, Enum
from dataclasses import dataclass
from threading import Thread, Event
from multiprocessing import Queue
from PySide6.QtCore import QMetaObject, Qt, QThread
from NodeGraphQt import BaseNode, Port, NodeBaseWidget
from qtwidgets.ui_local_media_player import LocalMediaPlayer
from data_classes import Dataset

# Import global constants and themes
from __init__ import *  # noqa


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


class InferencedTask(str, Enum):
    OBJECT_DETECTION = "Object Detection"
    IMAGE_SEGMENTATION = "Image Segmentation"
    IMAGE_CLASSIFICATION = "Image Classification"


class InputState(IntEnum):
    UNKNOWN = -1
    OK = 0
    WRONG_DTYPE = 2
    OUTPUT_ERROR = 3


class NodeState(IntEnum):
    IDLE = 0
    RUNNING = 1
    INTERNAL_ERROR = 2
    MISSING_CRITICAL_INPUT = 3
    CRITICAL_INPUT_ERROR = 4
    WAITING = 5


class ConnectionState(IntEnum):
    CONNECTED_OK = 1
    INCOMPATIBLE_CONNECTION = 0
    DISCONNECTED = 1


# =============================================================================
#  Custom widgets
# =============================================================================

class NodeWidgetWrapper(NodeBaseWidget):
    """Allows inserting a custom widget inside a node."""

    def __init__(self, name=None, label=None, parent=None, widget_class=None):
        super().__init__(parent)
        self.widget_class = widget_class
        self.value = None

        self.set_name(name)
        self.set_label(label)
        self.set_custom_widget(widget_class())

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value


# =============================================================================
#  FrontEnd / BackEnd base node classes
# =============================================================================

class FrontEndFlowDiPNode(BaseNode):
    """Frontend base node for FlowDiP."""

    __identifier__ = "com.flowdip"
    NODE_NAME = "Base FlowDiP Node"

    def __init__(self):
        super().__init__()
        self.default_color = ACTIVE_THEME["node_bg"]
        self.set_color(*self.default_color)

    # -------------------------------------------------------------------------
    def update_state(self, state: NodeState):
        """Updates the node color and state according to the current state."""
        self.state = state

        if state == NodeState.IDLE:
            self.set_color(*self.default_color)

        elif state == NodeState.RUNNING:
            self.set_color(*ACTIVE_THEME["node_running"])

        elif state in (
            NodeState.INTERNAL_ERROR,
            NodeState.MISSING_CRITICAL_INPUT,
            NodeState.CRITICAL_INPUT_ERROR,
        ):
            self.set_color(*ACTIVE_THEME["node_error"])

        elif state == NodeState.WAITING:
            # Lighten color to indicate waiting
            light_color = [min(255, int(c * 1.2)) for c in self.default_color]
            self.set_color(*light_color)

        self.update()

    # -------------------------------------------------------------------------
    def run(self):
        """Runs the node (delegated to backend)."""
        QMetaObject.invokeMethod(self.backend_node, "run", Qt.QueuedConnection)


class BackEndFlowDiPNode(Thread):
    """Backend node with execution logic in a separate thread."""

    def __init__(self, name: Optional[str] = None):
        super().__init__()
        self.name = name
        self.start_e = Event()
        self.done_e = Event()
        self._running = True

        self.dip_inputs: List["Input"] = []
        self.dip_outputs: List["Output"] = []
        self.state: NodeState = NodeState.IDLE

    # -------------------------------------------------------------------------
    def run(self):
        """Main execution loop."""
        while self._running:
            self.start_e.wait()
            self.start_e.clear()
            self.done_e.clear()

            self.execute()
            self.done_e.set()

    # -------------------------------------------------------------------------
    def execute(self):
        """Executes the dependency flow and the main node function."""
        self.update_state(NodeState.WAITING)

        # Validate critical inputs
        for input_port in self.dip_inputs:
            cs = input_port.check_connection()
            if input_port.connection_state != cs:
                input_port.connection_state = cs
                self.update_port(cs)

            if input_port.connection_state != ConnectionState.CONNECTED_OK and input_port.critical:
                self.update_state(NodeState.MISSING_CRITICAL_INPUT)
                return

        # Run dependent nodes
        for input_port in self.dip_inputs:
            if input_port.output and input_port.connection_state == ConnectionState.CONNECTED_OK:
                input_port.output.node.start_e.set()

        # Wait for dependencies
        for input_port in self.dip_inputs:
            if input_port.output and input_port.connection_state == ConnectionState.CONNECTED_OK:
                input_port.output.node.done_e.wait()
                if input_port.output.node.state != NodeState.IDLE and input_port.critical:
                    self.update_state(NodeState.CRITICAL_INPUT_ERROR)
                    return

        if self.state != NodeState.WAITING:
            return

        # Run main task
        self.update_state(NodeState.RUNNING)
        try:
            self._run()
        except Exception as e:
            print(f"Error in node '{self.name}': {e}")
            self.update_state(NodeState.INTERNAL_ERROR)

        if self.state == NodeState.RUNNING:
            self.update_state(NodeState.IDLE)

    # -------------------------------------------------------------------------
    def update_port(self, connection_state: ConnectionState):
        """Updates the visual state of the port (stub)."""
        pass

    def update_state(self, node_state: NodeState):
        """Updates the node state (stub)."""
        pass

    # -------------------------------------------------------------------------
    def create_port(self, name: str, is_input: bool = True, critical: bool = False) -> Port:
        """Creates an input or output port with FlowDiP metadata."""
        port = self.add_input(name) if is_input else self.add_output(name)

        if is_input:
            input_port = Input(name, critical)
            input_port.port = port
            self.dip_inputs.append(input_port)
            return input_port
        else:
            output_port = Output()
            output_port.port = port
            self.dip_outputs.append(output_port)
            return output_port

    # -------------------------------------------------------------------------
    def _run(self):
        """Method to be overridden by subclasses."""
        pass


# =============================================================================
#  Input/Output classes
# =============================================================================

class Input:
    """Represents a FlowDiP input port."""

    def __init__(self, name: str, critical: bool = False):
        self.name = name
        self.output: Optional["Output"] = None
        self.critical = critical
        self.state = InputState.UNKNOWN
        self.connection_state = ConnectionState.DISCONNECTED
        self.tooltip: Optional[str] = None
        self.datatype: Optional[type] = None
        self.accepted_types: List[type] = []

    def check_connection(self) -> ConnectionState:
        """Validates the connection state with its output."""
        if not self.output:
            return ConnectionState.DISCONNECTED

        if not set(self.output.possible_types) & set(self.accepted_types):
            return ConnectionState.INCOMPATIBLE_CONNECTION

        return ConnectionState.CONNECTED_OK


class Output:
    """Represents a FlowDiP output port."""

    def __init__(self):
        self.tooltip: Optional[str] = None
        self.connection_state = ConnectionState.DISCONNECTED
        self.data = None
        self.datatype: Optional[type] = None
        self.possible_types: List[type] = []


# =============================================================================
#  Specific nodes
# =============================================================================

class DatasetGenerator(FrontEndFlowDiPNode):
    NODE_NAME = "Dataset Generator"

    def __init__(self):
        super().__init__()
        self.dataset: Optional[Dataset] = None


class MediaPlayer(FrontEndFlowDiPNode):
    __identifier__ = "com.flowdip"
    NODE_NAME = "Media Player"

    def __init__(self):
        super().__init__()
        widget = NodeWidgetWrapper(
            name="media_player",
            widget_class=LocalMediaPlayer,
            parent=self.view
        )
        self.add_custom_widget(widget=widget, tab="Custom")


# =============================================================================
#  FrontEnd / BackEnd Managers
# =============================================================================

class BackEndManager(Thread):
    """Handles the backend request queue."""

    def __init__(self, req_queue: Queue, event_queue: Queue):
        super().__init__()
        self.req_queue = req_queue
        self.event_queue = event_queue
        self._running = True

    def run(self):
        while self._running:
            req = self.req_queue.get()
            if req.request_type == RequestType.SHUTDOWN:
                self._running = False
            else:
                self.handle_request(req)

    def handle_request(self, request: Request):
        pass


class FrontEndManager(QThread):
    """Handles frontend events."""

    def __init__(self, req_queue: Queue, event_queue: Queue):
        super().__init__()
        self.req_queue = req_queue
        self.event_queue = event_queue
        self._running = True

    def run(self):
        while self._running:
            ev = self.event_queue.get()
            if ev.event_type == EventType.SHUTDOWN:
                self._running = False
            else:
                self.handle_event(ev)

    def handle_event(self, ev: Event):
        pass

