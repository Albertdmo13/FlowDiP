from platform import node
import uuid

from NodeGraphQt import NodeBaseWidget, BaseNode, NodeGraph
from PySide6.QtCore import Qt, QMetaObject
from typing import Optional, Any, TYPE_CHECKING
from flowdip.backend.flowdip_be_base import NodeState
from flowdip import Request, RequestType, CreateNodePayload, DeleteNodePayload
from flowdip import get_logger

# =============================================================================
#  Custom NodeGraph
# =============================================================================
class FlowDiPNodeGraph(NodeGraph):
    """Wrapper for NodeGraph to add custom functionality if needed."""

    def __init__(self, fe_manager):
        super().__init__()
        self.fe_manager = fe_manager
        self.logger = get_logger(self.__class__.__name__)  # logger by class name

    def create_node(
        self,
        node_type: str,
        name: Optional[str] = None,
        selected: bool = True,
        color: Any | None = None,
        text_color: Any | None = None,
        pos: Any | None = None,
        push_undo: bool | None = None,
    ) -> Any:
        node = super().create_node(node_type, name, selected, color,
                                   text_color, pos, push_undo)

        if isinstance(node, FrontFlowDiPNode):
            self.logger.info(f"Node [{node.name()}] created. Requesting backend node.")
            node.request_backend_node(self.fe_manager)

        return node
    
    def cut_nodes(self, nodes=None):
        super().cut_nodes(nodes)
        self.logger.info(f"[Node Graph] : Nodes cut event triggered")
        if nodes is not None:
            for node in nodes:
                self.delete_backend_node(node)
    
    def remove_node(self, node, push_undo=True):
        self.logger.info(f"[Node Graph] : Node remove event triggered")
        self.delete_backend_node(node)
        return super().remove_node(node, push_undo)

    def remove_nodes(self, nodes, push_undo=True):
        self.logger.info(f"[Node Graph] : Nodes remove event triggered")
        for node in nodes:
            self.delete_backend_node(node)
        return super().remove_nodes(nodes, push_undo)
    
    def delete_node(self, node: BaseNode, push_undo: bool = True) -> None:
        self.logger.info(f"[Node Graph] : Node delete event triggered")
        self.delete_backend_node(node)
        return super().delete_node(node, push_undo)

    def delete_nodes(self, nodes, push_undo=True):
        self.logger.info(f"[Node Graph] : Nodes delete event triggered")
        for node in nodes:
            self.delete_backend_node(node)
        return super().delete_nodes(nodes, push_undo)

    def delete_backend_node(self, node):
        """Requests the backend manager to delete the corresponding backend node."""
        if isinstance(node, FrontFlowDiPNode):
            self.logger.info(f"Requesting backend to delete node: {node.name()}")
            self.fe_manager.publish_request(Request(
                request_type=RequestType.DELETE_NODE,
                payload=DeleteNodePayload(
                    node_class_name=node.be_node_class.__name__,
                    flowdip_name=node.flowdip_name
                )
            ))


# =============================================================================
#  Custom widgets
# =============================================================================
class FlowDiPNodeWidget(NodeBaseWidget):
    """Allows inserting a custom widget inside a node."""

    def __init__(self, name=None, label=None, parent=None, widget_class=None):
        super().__init__(parent)
        self.widget_class = widget_class
        self.value = None
        self.logger = get_logger(self.__class__.__name__)  # logger by class name

        self.set_name(name)
        self.set_label(label)
        self.set_custom_widget(widget_class())

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.logger.debug(f"Value set on widget {self.get_name()}: {value}")
        self.value = value


class FrontFlowDiPNode(BaseNode):
    """Frontend base node for FlowDiP."""

    __identifier__ = "flowdip"
    NODE_NAME = "Base FlowDiP Node"

    # Overwritable class attributes
    widget_class = None
    be_node_class = None
    loop = True

    def __init__(self):
        super().__init__()
        self.active_theme = None
        self.fe_manager = None
        self.flowdip_name = self.generate_flowdip_name()
        # logger uses node's name instead of class name
        self.logger = get_logger(self.name())

        if self.widget_class is not None:
            widget = FlowDiPNodeWidget(
                name=self.name(),
                widget_class=self.widget_class,
                parent=self.view
            )
            self.add_custom_widget(widget=widget)
            self.logger.info(f"Custom widget added to node {self.name()}")

    def request_backend_node(self, fe_manager):
        """Requests the backend manager to create the corresponding backend node."""
        self.fe_manager = fe_manager
        self.logger.info(f"Requesting backend node for {self.name()}")

        if self.be_node_class is not None:
            self.fe_manager.publish_request(Request(
                request_type=RequestType.CREATE_NODE,
                payload=CreateNodePayload(
                    node_class_name=self.be_node_class.__name__,
                    flowdip_name=self.flowdip_name,
                    loop=self.loop
                )
            ))

    def update_state(self, state: NodeState):
        """Updates the node color and state according to the current state."""
        self.state = state
        self.logger.debug(f"Updating state of {self.flowdip_name} to {state.name}")

        if state == NodeState.IDLE:
            self.set_color(*self.default_color)
        elif state == NodeState.RUNNING:
            self.set_color(*self.active_theme["node_running"])
        elif state in (
            NodeState.INTERNAL_ERROR,
            NodeState.MISSING_CRITICAL_INPUT,
            NodeState.CRITICAL_INPUT_ERROR,
        ):
            self.set_color(*self.active_theme["node_error"])
        elif state == NodeState.WAITING:
            light_color = [min(255, int(c * 1.2)) for c in self.default_color]
            self.set_color(*light_color)

        self.update()

    def generate_flowdip_name(self) -> str:
        """Generates a FlowDiP name. FlowDiP names are used to link the
        FrontEnd Node class and BackEnd node class. They are unique for each node
        and are created on node instantiation. They are immutable.
        Format: flowdip.<ClassName>.<UUID>
        Example: flowdip.FrontMediaPlayer.d4c9651a-dbec-4227-a3a4-132c97dfe66f
        """
        return (self.__identifier__ + "."
                + self.__class__.__name__.removeprefix("Front") + "."
                + str(uuid.uuid4()))

    def run(self):
        """Runs the node (delegated to backend)."""
        self.logger.info(f"Running node {self.name()}")
        QMetaObject.invokeMethod(self.backend_node, "run", Qt.QueuedConnection)
