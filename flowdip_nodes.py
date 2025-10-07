from typing import List, Optional
from uuid import uuid4

from data_classes import Dataset, Image, ImageGroup
from enum import IntEnum

from NodeGraphQt import NodeGraph, BaseNode

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
    FINISHED = 5

class ConnectionState(IntEnum):
    # Before running
    CONNECTED_OK = 1
    INCOMPATIBLE_CONNECTION = 0
    DISCONNECTED = 1

class FlowDiPNode(BaseNode):

    __identifier__ = 'flowdip'

    def __init__(self):
        super().__init__()

        self.inputs: List[Input] = []
        self.outputs: List[Output] = []
        self.state: NodeState = NodeState.IDLE

    def run(self):

        self.state = NodeState.RUNNING

        # Make sure all critical inputs are connected and OK
        for input in self.inputs:
            input.connection_state = input.check_connection()
            if input.connection_state != ConnectionState.CONNECTED_OK and input.critical:
                self.state = NodeState.MISSING_CRITICAL_INPUT
                return 
        
        # If any critical input is missing or has an error, do not run
        if NodeState.RUNNING != self.state:
            return

        # Run all dependant nodes
        for input in self.inputs:
            if input.output is not None and input.connection_state == ConnectionState.CONNECTED_OK:
                input.output.node.run()
                if input.output.node.state != NodeState.FINISHED and input.critical:
                    self.state = NodeState.CRITICAL_INPUT_ERROR
                    return

        self.state = self._run()

        return
    
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
    
    def check_state(self) -> InputState:
        if self.connection_state != ConnectionState.CONNECTED_OK or self.output is None:
            return InputState.UNKNOWN
        else:
            if self.output.node.state != NodeState.IDLE and self.output.node.state != NodeState.FINISHED:
                return InputState.OUTPUT_ERROR
            if self.output.node.state == NodeState.IDLE:
                return InputState.UNKNOWN
            if self.output.datatype not in self.accepted_types:
                return InputState.WRONG_DTYPE
            
        return InputState.OK


class Output():
    def __init__(self, name: str, node: FlowDiPNode):
        self.name: str = name
        self.node: FlowDiPNode = node
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

AVAILABLE_NODE_TYPES = [DatasetGenerator]
NODE_TYPE_MAP = {cls.__name__: cls for cls in AVAILABLE_NODE_TYPES}
