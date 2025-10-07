# -*- coding: utf-8 -*-
"""
FlowDip — Node Graph editor using PySide6 + NodeGraphQt.
Starts with a docked Nodes Palette on the left, no menu bar.
Uses global CSS for UI and Python theme variables for NodeGraph.
"""
import os
from urllib import request
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QDockWidget
from NodeGraphQt import NodeGraph, BaseNode, NodeGraphMenu, NodesPaletteWidget

from hotkey_functions import *  # if needed
import flowdip_nodes


from multiprocessing import Process, Queue

from __init__ import *  # to load themes and global constants

# Helper to recursively set stylesheets for context menus
def set_context_menu_stylesheet(menu):
    if isinstance(menu, NodeGraphMenu):
        menu.qmenu.setStyleSheet(GLOBAL_STYLESHEET)
        for item in menu.get_items():
            set_context_menu_stylesheet(item)

# ----------------------------------------------------------------------
# Main Application Window
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    """Main application window with NodeGraph viewer and docked palette."""

    def __init__(self, fe_manager: flowdip_nodes.FrontEndManager):
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
            if isinstance(flowdip_node, type) and issubclass(flowdip_node, flowdip_nodes.FrontEndFlowDiPNode):
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
def main_frontend(request_queue, response_queue):

    app = QApplication([])

    # Load CSS stylesheet
    css_path = ACTIVE_THEME["css"]
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            GLOBAL_STYLESHEET = f.read()
        app.setStyleSheet(GLOBAL_STYLESHEET)
        print(f"Loaded stylesheet: {css_path}")
    else:
        print(f"Stylesheet not found: {css_path}")

    # Create frontend manager thread
    fe_manager = flowdip_nodes.FrontEndManager(request_queue, response_queue)
    fe_manager.start()

    # Launch main window
    window = MainWindow(fe_manager)
    if GLOBAL_STYLESHEET:
        window.setStyleSheet(GLOBAL_STYLESHEET)
    window.show()

    app.exec()

    fe_manager.event_queue.put(flowdip_nodes.Event(event_type=flowdip_nodes.EventType.SHUTDOWN, payload=None))
    fe_manager.req_queue.put(flowdip_nodes.Request(request_type=flowdip_nodes.RequestType.SHUTDOWN, payload=None))

    fe_manager.wait()


def main_backend(request_queue, response_queue):

    be_manager = flowdip_nodes.BackEndManager(request_queue, response_queue)
    be_manager.start()
    be_manager.join()

if __name__ == "__main__":

    request_queue = Queue()
    response_queue = Queue()

    backend_process = Process(target=main_backend, args=(request_queue, response_queue), daemon=True)
    backend_process.start()

    frontend_process = Process(target=main_frontend, args=(request_queue, response_queue), daemon=False)
    frontend_process.start()

    # Join processes
    frontend_process.join()
    backend_process.join()

