
from typing import Any, List, Optional
from enum import IntEnum, Enum
from threading import Thread, Event

# =============================================================================
#  Enums and data structures
# =============================================================================

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
#  Input/Output classes
# =============================================================================

# --- Clase base ---
class Port:
    """Base class for FlowDiP ports (Input/Output)."""

    def __init__(self, datatypes: Optional[List[type]] = None):
        self.tooltip: Optional[str] = None
        self.connection_state = ConnectionState.DISCONNECTED
        self.datatypes: List[type] = datatypes if datatypes is not None else []

# --- Subclase Input ---
class Input(Port):
    """Represents a FlowDiP input port."""

    def __init__(self, name: str, critical: bool = False, datatype: Optional[type] = None):
        super().__init__(datatype=datatype)
        self.name = name
        self.output: Optional[Output] = None
        self.critical = critical
        self.state = InputState.UNKNOWN

    def check_connection(self) -> ConnectionState:
        """Validates the connection state with its output."""
        if not self.output:
            return ConnectionState.DISCONNECTED

        if not set(self.output.datatypes) & set(self.datatypes):
            return ConnectionState.INCOMPATIBLE_CONNECTION

        return ConnectionState.CONNECTED_OK


# --- Subclase Output ---
class Output(Port):
    """Represents a FlowDiP output port."""

    def __init__(self, datatypes: Optional[List[type]] = None):
        super().__init__(datatypes=datatypes)
        self.data = None
        self.input: Optional[Input] = None

class BackEndFlowDiPNode(Thread):
    """Backend node with execution logic in a separate thread."""

    def __init__(self, flowdip_name: Optional[str] = None, loop: bool = False):
        super().__init__()
        self.flowdip_name = flowdip_name
        self.start_e = Event()
        self.done_e = Event()
        self._running = True
        self._sync = False # If true, waits for dependant nodes to finish before proceeding
        self.dip_inputs: List[Input] = []
        self.dip_outputs: List[Output] = []
        self.state: NodeState = NodeState.IDLE
        self._loop = loop

    # -------------------------------------------------------------------------
    def run(self):
        """Main execution loop."""
        while self._running:
            if self._loop is True:
                self.start_e.wait()
                # Loop nodes don't clear their start event,
                # they run in a constant loop. Only user
                # action can clear and set the event, essentially
                # pausing and resuming the loop.
            else:
                self.start_e.wait()
                self.start_e.clear()

            self.process_data()
            self.done_e.set()

    # -------------------------------------------------------------------------
    def process_data(self):
        """Executes the dependency flow and the main node function."""

        # Validate inputs -----------------------------------------------------

        # Check and update connection states
        for input_port in self.dip_inputs:
            cs = input_port.check_connection()
            if input_port.connection_state != cs:
                input_port.connection_state = cs
                self.update_port_state(cs)

        # Make sure all critical inputs are connected and have data
        for input_port in self.dip_inputs:
            if input_port.critical:
                if input_port.output and input_port.connection_state == ConnectionState.CONNECTED_OK:
                        # Execute to fulfill dependency
                        if (input_port.data is None):
                            # If no data, run dependency and wait
                            self.update_state(NodeState.WAITING)
                            input_port.output.node.done_e.clear()
                            input_port.output.node.start_e.set()
                            input_port.output.node.done_e.wait()
                else:
                        self.update_state(NodeState.MISSING_CRITICAL_INPUT)
                        return

        # Run main task
        self.update_state(NodeState.RUNNING)
        try:
            self._process_data()
        except Exception as e:
            print(f"Error in node '{self.flowdip_name}': {e}")
            self.update_state(NodeState.INTERNAL_ERROR)

        # Propagate execution toward output nodes ----------------------------

        # Once processing is done, trigger all output nodes to process
        for output_port in self.dip_outputs:
            output_port.node.done_e.clear()
            output_port.node.start_e.set()

        # If sync is active. Wait for outputs to finish
        if self._sync:
            self.update_state(NodeState.WAITING)
            for output_port in self.dip_outputs:
                output_port.node.done_e.wait()

        self.update_state(NodeState.IDLE)

    def update_port_data(output_port: Output, data: Any):
        """Updates the data of an output port."""
        output_port.data = data
        output_port.input.data = data

    # -------------------------------------------------------------------------
    def update_port_state(self, connection_state: ConnectionState):
        """Updates the visual state of the port (stub)."""
        pass

    def update_state(self, node_state: NodeState):
        """Updates the node state (stub)."""
        pass

    # -------------------------------------------------------------------------
    def create_port(self, flowdip_name: str, is_input: bool = True, critical: bool = False) -> Port:
        """Creates an input or output port with FlowDiP metadata."""
        port = self.add_input(flowdip_name) if is_input else self.add_output(flowdip_name)

        if is_input:
            input_port = Input(flowdip_name, critical)
            input_port.port = port
            self.dip_inputs.append(input_port)
            return input_port
        else:
            output_port = Output()
            output_port.port = port
            self.dip_outputs.append(output_port)
            return output_port

    # -------------------------------------------------------------------------
    def _process_data(self):
        """Method to be overridden by subclasses."""
        pass
