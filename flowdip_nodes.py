from time import sleep
from typing import List, Optional
from uuid import uuid4
from PySide6.QtWidgets import QApplication

from data_classes import Dataset, Image, ImageGroup
from enum import IntEnum, Enum

from NodeGraphQt import NodeGraph, BaseNode, Port
from __init__ import *  # to load themes and global constants

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

class FlowDiPNode(BaseNode):

    __identifier__ = 'flowdip'

    def __init__(self):
        super().__init__()

        # Set node color using theme
        self.default_color = ACTIVE_THEME["node_bg"]
        self.set_color(*self.default_color)

        self.dip_inputs: List[Input] = []
        self.dip_outputs: List[Output] = []
        self.state: NodeState = NodeState.IDLE

        # Add 'Run' button
        self.add_button(name='Run', text='Run')
        btn = self.get_widget('Run')

        if GLOBAL_STYLESHEET:
            btn._button.setStyleSheet(GLOBAL_STYLESHEET)

        btn.setToolTip('Execute this node')
        btn._button.clicked.connect(self.run)

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
        QApplication.processEvents()

    def run(self):
        print(self.dip_inputs)
        self.update_state(NodeState.WAITING)

        # Make sure all critical dip_inputs are connected and OK
        for input in self.dip_inputs:
            input.connection_state = input.check_connection()
            if input.connection_state != ConnectionState.CONNECTED_OK and input.critical:
                self.update_state(NodeState.MISSING_CRITICAL_INPUT)
                return 
        
        # If any critical input is missing or has an error, do not run
        if NodeState.WAITING != self.state:
            return

        # Run all dependant nodes
        for input in self.dip_inputs:
            if input.output is not None and input.connection_state == ConnectionState.CONNECTED_OK:
                input.output.node.run()
                if input.output.node.state != NodeState.IDLE and input.critical:
                    self.update_state(NodeState.CRITICAL_INPUT_ERROR)
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
    def __init__(self, critical: bool = False, port: Optional[Port] = None):

        self.port = port

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
    def __init__(self, port: Optional[Port] = None):
        super().__init__()
        self.port = port
        self.tooltip: Optional[str] = None
        self.connection_state: ConnectionState = ConnectionState.DISCONNECTED
        self.data = None
        self.datatype: Optional[type] = None
        self.possible_types: List[type] = []

class DatasetGenerator(FlowDiPNode):
    NODE_NAME = "Dataset Generator"

    def __init__(self):
        super().__init__()
        self.dataset: Optional[Dataset] = None

        self.create_port(name="Dataset", is_input=False)
        self.create_port(name="Images", is_input=True, critical=True)

    def _run(self):
        sleep(1)  # Simulate processing time