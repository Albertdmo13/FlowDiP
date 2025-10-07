from time import sleep
from typing import List, Optional, Any
from uuid import uuid4
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QThread, QMetaObject, Qt, Slot

from data_classes import Dataset, Image, ImageGroup
from enum import IntEnum, Enum

from NodeGraphQt import NodeGraph, BaseNode, Port
from __init__ import *  # to load themes and global constants
from threading import Thread, Event

from multiprocessing import Queue

class RequestType(IntEnum):
    CREATE_NODE = 0
    EDIT_NODE = 1
    RUN_NODE = 2

class EventType(IntEnum):
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
    # Before running
    CONNECTED_OK = 1
    INCOMPATIBLE_CONNECTION = 0
    DISCONNECTED = 1


class FrontEndFlowDiPNode(BaseNode):

    def __init__(self):
        super().__init__()

        # Set node color using theme
        self.default_color = ACTIVE_THEME["node_bg"]
        self.set_color(*self.default_color)

        # Add 'Run' button
        self.add_button(name='Run', text='Run')
        btn = self.get_widget('Run')

        if GLOBAL_STYLESHEET:
            btn._button.setStyleSheet(GLOBAL_STYLESHEET)

        btn.setToolTip('Execute this node')
        btn._button.clicked.connect(self.run)

        self.update()

    def update_state(self, state: NodeState):
        self.state = state
        if state == NodeState.IDLE:
            self.set_color(*self.default_color)
        elif state == NodeState.RUNNING:
            self.set_color(*ACTIVE_THEME["node_running"])
        elif (state == NodeState.INTERNAL_ERROR or state == NodeState.MISSING_CRITICAL_INPUT
              or state == NodeState.CRITICAL_INPUT_ERROR):
            self.set_color(*ACTIVE_THEME["node_error"])
        elif state == NodeState.WAITING:
            default_light_color = [min(255, c*1.2) for c in self.default_color]
            self.set_color(*default_light_color)  # Lighten

        self.update()

    def run(self):
        # delegate to backend thread
        QMetaObject.invokeMethod(self.backend_node, "run", Qt.QueuedConnection)

class BackEndFlowDiPNode(Thread):

    def __init__(self, name:Optional[str] = None):
        super().__init__()

        self.name = name

        self.start_e = Event()
        self.done_e = Event()

        self.dip_inputs: List[Input] = []
        self.dip_outputs: List[Output] = []
        self.state: NodeState = NodeState.IDLE

    def run(self):
        """Execution loop"""
        while self._running is True:
            # Wait for start event trigger
            self.start_e.wait()
            self.start_e.clear()
            self.done_e.clear()

            self.execute()

            # Trigger done for waiting events
            self.done_e.set()

    def execute(self):

        self.update_state(NodeState.WAITING)

        # Make sure all critical dip_inputs are connected and OK
        for input in self.dip_inputs:
            cs = input.check_connection()
            if input.connection_state != cs:
                input.connection_state = cs
                self.update_port(cs)

            # If critical input is not properly connected abort execution
            if input.connection_state != ConnectionState.CONNECTED_OK and input.critical:
                self.update_state(NodeState.MISSING_CRITICAL_INPUT)
                return 

        # Run all dependant nodes
        for input in self.dip_inputs:
            if input.output is not None and input.connection_state == ConnectionState.CONNECTED_OK:
                input.output.node.start_e.set()

        # Wait for all dependant nodes to finish execution
        for input in self.dip_inputs:
            if input.output is not None and input.connection_state == ConnectionState.CONNECTED_OK:
                input.output.node.done_e.wait()
                if input.output.node.state != NodeState.IDLE and input.critical:
                    self.update_state(NodeState.CRITICAL_INPUT_ERROR)
                    return

        # If any critical input is missing or has an error, do not run
        if NodeState.WAITING != self.state:
            return
               
        self.update_state(NodeState.RUNNING)
        try:
            self._run()
        except Exception as e:
            print(f"Error occurred while running node '{self.name()}': {e}")
            self.update_state(NodeState.INTERNAL_ERROR)

        if self.state == NodeState.RUNNING:
            self.update_state(NodeState.IDLE)

        return
    
    def update_port(self, connection_state: ConnectionState):
        pass

    def update_state(self, node_state: NodeState):
        pass

    def create_port(self, name: str, is_input: bool = True, critical: bool = False) -> Port:
        # Create NodeGraph port
        port = self.add_input(name) if is_input else self.add_output(name)

        # Wrap it in Input/Output class
        if is_input:
            input = Input(port=port, critical=critical)
            self.dip_inputs.append(input)
            return input
        else:
            output = Output(port=port)
            self.dip_outputs.append(output)
            return output

    def _run(self):
        # To be implemented in subclasses
        pass    

class Input():
    def __init__(self, name: str, critical: bool = False):

        self.name: str = name
        self.output: Optional[Output] = None
        self.critical: bool = critical
        self.state: InputState = InputState.UNKNOWN
        self.connection_state: ConnectionState = ConnectionState.DISCONNECTED
        self.tooltip: Optional[str] = None
        self.datatype: Optional[type] = None
        self.accepted_types: List[type] = []

    def check_connection(self) -> ConnectionState:
        if self.output is None:
            return ConnectionState.DISCONNECTED
        else:
            if len(set(self.output.possible_types) & set(self.accepted_types)) == 0:
                return ConnectionState.INCOMPATIBLE_CONNECTION
            
        return ConnectionState.CONNECTED_OK

class Output():
    def __init__(self):
        super().__init__()
        self.tooltip: Optional[str] = None
        self.connection_state: ConnectionState = ConnectionState.DISCONNECTED
        self.data = None
        self.datatype: Optional[type] = None
        self.possible_types: List[type] = []

class DatasetGenerator(FrontEndFlowDiPNode):
    NODE_NAME = "Dataset Generator"

    def __init__(self):
        super().__init__()
        self.dataset: Optional[Dataset] = None

class BackEndManager(Thread):
    def __init__(self, req_queue: Queue, event_queue: Queue):
        self.req_queue = req_queue
        self.event_queue = event_queue
        self._running = True

    def run(self):
        while self._running is True:
            req = self.req_queue.get()
            self.handle_request()

    def handle_request(self, request):
        pass

class FrontEndManager(QThread):
    def __init__(self, req_queue: Queue, event_queue: Queue):
        self.req_queue = req_queue
        self.event_queue = event_queue
        self._running = True

    def run(self):
        while self._running is True:
            req = self.req_queue.get()
            self.handle_request()

    def handle_request(self, request):
        pass