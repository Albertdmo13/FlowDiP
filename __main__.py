# -*- coding: utf-8 -*-
"""
FlowDip — Node Graph editor using PySide6 + NodeGraphQt.
Starts with a docked Nodes Palette on the left, no menu bar.
Uses global CSS for UI and Python theme variables for NodeGraph.
"""
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from NodeGraphQt import NodeGraph, BaseNode, NodeGraphMenu, NodesPaletteWidget

from hotkey_functions import *  # if needed
import flowdip_nodes

# ----------------------------------------------------------------------
# Global Constants
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(__file__)
MENU_JSON_PATH = os.path.join(BASE_DIR, "hotkeys.json")
THEMES_DIR = os.path.join(BASE_DIR, "themes")

# ----------------------------------------------------------------------
# Theme Color Palettes
# ----------------------------------------------------------------------
GRAY = {
    "background": (34, 34, 34),   # NodeGraph background color
    "grid": (85, 85, 85),         # NodeGraph grid color
    "node_bg": (58, 58, 58),      # Node body color
    "node_border": (100, 100, 100),
    "accent": (108, 158, 255),
    "text": (224, 224, 224),
    "css": os.path.join(THEMES_DIR, "gray.css"),
}

DARK_BLUE = {
    "background": (28, 32, 40),      # Darker background
    "grid": (45, 52, 66),            # Darker grid
    "node_bg": (50, 52, 65),         # Darker node body
    "node_border": (65, 80, 100),    # Darker node border
    "accent": (100, 140, 210),       # Muted accent
    "text": (210, 220, 235),         # Softer text
    "css": os.path.join(THEMES_DIR, "dark_blue.css"),
}

# Set active theme
ACTIVE_THEME = DARK_BLUE

# ----------------------------------------------------------------------
# Global stylesheet (loaded at runtime)
# ----------------------------------------------------------------------
GLOBAL_STYLESHEET = ""

# Helper to recursively set stylesheets for context menus
def set_context_menu_stylesheet(menu):
    if isinstance(menu, NodeGraphMenu):
        menu.qmenu.setStyleSheet(GLOBAL_STYLESHEET)
        for item in menu.get_items():
            set_context_menu_stylesheet(item)

# ----------------------------------------------------------------------
# Custom Node Definition
# ----------------------------------------------------------------------
class MyNode(BaseNode):
    """Custom FlowDip node with input/output ports and a 'Run' button."""

    __identifier__ = 'flowdip'
    NODE_NAME = 'FlowDip Node'

    def __init__(self):
        super().__init__()

        # Set node color using theme
        r, g, b = ACTIVE_THEME["node_bg"]
        self.set_color(r, g, b)

        # Ports
        self.add_input('Input')
        self.add_output('Output')

        # Add 'Run' button
        self.add_button(name='Run', text='Run')
        btn = self.get_widget('Run')

        if GLOBAL_STYLESHEET:
            btn._button.setStyleSheet(GLOBAL_STYLESHEET)

        btn.setToolTip('Execute this node')
        btn._button.clicked.connect(self.on_run_pressed)

    def on_run_pressed(self):
        """Callback executed when 'Run' button is clicked."""
        print(f"Node '{self.name()}' executed.")


# ----------------------------------------------------------------------
# Main Application Window
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    """Main application window with NodeGraph viewer and docked palette."""

    def __init__(self):
        super().__init__()

        # ------------------ Graph Setup ------------------
        self.graph = NodeGraph()
        self.graph.set_context_menu_from_file(MENU_JSON_PATH)

        # Apply theme colors
        bg = ACTIVE_THEME["background"]
        grid = ACTIVE_THEME["grid"]
        self.graph.set_background_color(*bg)
        self.graph.set_grid_color(*grid)

        # Register FlowDiP nodes
        for flowdip_node in flowdip_nodes.__dict__.values():
            if isinstance(flowdip_node, type) and issubclass(flowdip_node, flowdip_nodes.FlowDiPNode):
                self.graph.register_node(flowdip_node)

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

        # Create default node
        # self.graph.create_node('com.flowdip.MyNode', name='Node A', pos=(100, 100))

        # Add and attach the Node Palette by default
        self._create_nodes_palette()

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


# ----------------------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------------------
def main():
    global GLOBAL_STYLESHEET

    app = QApplication([])

    # Load CSS stylesheet
    css_path = ACTIVE_THEME["css"]
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            GLOBAL_STYLESHEET = f.read()
        app.setStyleSheet(GLOBAL_STYLESHEET)
        print(f"✅ Loaded stylesheet: {css_path}")
    else:
        print(f"⚠️ Stylesheet not found: {css_path}")

    # Launch main window
    window = MainWindow()
    if GLOBAL_STYLESHEET:
        window.setStyleSheet(GLOBAL_STYLESHEET)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
