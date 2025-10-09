from xml.dom import Node
from NodeGraphQt import NodeBaseWidget, BaseNode, NodeGraph
from PySide6.QtCore import Qt, QMetaObject
from typing import Optional, Any
from flowdip.backend.flowdip_be_base import NodeState

# =============================================================================
#  Custom NodeGraph
# =============================================================================
NodeGraph.create_node
class FlowDiPNodeGraph(NodeGraph):
    """Wrapper for NodeGraph to add custom functionality if needed."""
    def __init__(self):
        super().__init__()

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

        if isinstance(node, FrontEndFlowDiPNode):
            print("Custom setup for FlowDiP node for node {name}".format(name=node.name()))

        return node
# =============================================================================
#  Custom widgets
# =============================================================================

class FlowDiPNodeWidget(NodeBaseWidget):
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

class FrontEndFlowDiPNode(BaseNode):
    """Frontend base node for FlowDiP."""

    __identifier__ = "com.flowdip"
    NODE_NAME = "Base FlowDiP Node"

    def __init__(self, widget_class: Optional[Any] = None, be_node_class: Optional[Any] = None):
        super().__init__()
        self.active_theme = None

        if widget_class is not None:
            widget = FlowDiPNodeWidget(
                name="media_player",
                widget_class=widget_class,
                parent=self.view
            )
            self.add_custom_widget(widget=widget)


    # -------------------------------------------------------------------------
    def update_state(self, state: NodeState):
        """Updates the node color and state according to the current state."""
        self.state = state

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
            # Lighten color to indicate waiting
            light_color = [min(255, int(c * 1.2)) for c in self.default_color]
            self.set_color(*light_color)

        self.update()

    # -------------------------------------------------------------------------
    def run(self):
        """Runs the node (delegated to backend)."""
        QMetaObject.invokeMethod(self.backend_node, "run", Qt.QueuedConnection)
