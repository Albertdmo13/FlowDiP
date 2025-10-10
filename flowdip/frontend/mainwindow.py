from typing import TYPE_CHECKING

from flowdip.frontend.constants import (
    GLOBAL_STYLESHEET,
    ACTIVE_THEME,
    MENU_JSON_PATH,
)
from flowdip.frontend.utils import set_context_menu_stylesheet

from flowdip.frontend.flowdip_fe_base import FlowDiPNodeGraph
import flowdip.frontend.flowdip_nodes as FlowDiPNodes
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QMainWindow,
    QDockWidget,
)
from NodeGraphQt import NodesPaletteWidget, BaseNode

# ----------------------------------------------------------------------
# Main Application Window
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    """Main application window with NodeGraph viewer and docked palette."""

    def __init__(self, fe_manager):
        super().__init__()

        # ------------------ Graph Setup ------------------
        self.graph = FlowDiPNodeGraph(fe_manager)
        self.graph.set_context_menu_from_file(MENU_JSON_PATH)

        # Apply theme colors
        bg = ACTIVE_THEME["background"]
        grid = ACTIVE_THEME["grid"]
        self.graph.set_background_color(*bg)
        self.graph.set_grid_color(*grid)
        self.graph.node_created.connect(self.update_node)

        # Register FlowDiP nodes
        for node_class in FlowDiPNodes.__dict__.values():
            if isinstance(node_class, type) and issubclass(node_class, FlowDiPNodes.FrontFlowDiPNode):
                self.graph.register_node(node_class)

        # Viewer setup
        self.viewer = self.graph.widget
        if GLOBAL_STYLESHEET:
            self.viewer.setStyleSheet(GLOBAL_STYLESHEET)
            set_context_menu_stylesheet(self.graph.context_menu())

        # ------------------ Window Setup ------------------
        self.setWindowTitle("FlowDip")
        self.resize(1600, 900)
        self.setCentralWidget(self.viewer)
        self._extend_context_menu()

        # Add and attach the Node Palette by default
        self._create_nodes_palette()

    def update_node(self, node: BaseNode):
        if isinstance(node, FlowDiPNodes.FrontFlowDiPNode):

            node.active_theme = ACTIVE_THEME
            node.set_color(*ACTIVE_THEME["node_bg"])

    # ------------------------------------------------------------------
    def _extend_context_menu(self):
        """Extend background right-click menu with extra actions."""
        menu = self.graph.context_menu()
        menu.add_separator()
        menu.add_command("Add Node", self._on_add_node)
        menu.add_command("Open Nodes Palette", self._on_open_node_palette)

    # ------------------------------------------------------------------
    def _on_add_node(self):
        """Adds a new node at the cursor position."""
        viewer = self.graph.viewer()
        cursor_pos = QCursor.pos()
        local_pos = viewer.mapFromGlobal(cursor_pos)
        scene_pos = viewer.mapToScene(local_pos)

        self.graph.create_node(
            'com.flowdip.MyNode',
            name='New Node',
            pos=(scene_pos.x(), scene_pos.y())
        )
        print(f"New node added at ({scene_pos.x():.0f}, {scene_pos.y():.0f})")

    # ------------------------------------------------------------------
    def _on_open_node_palette(self):
        """Opens a floating Nodes Palette."""
        dock = self._create_nodes_palette(floating=True)
        dock.show()

    # ------------------------------------------------------------------
    def _create_nodes_palette(self, floating: bool = False):
        """Creates and attaches a Nodes Palette dock."""
        dock = QDockWidget("Nodes Palette", self)
        dock.setWidget(NodesPaletteWidget(node_graph=self.graph))
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFloating(floating)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        return dock
