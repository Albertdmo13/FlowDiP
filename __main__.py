# -*- coding: utf-8 -*-
"""
Dark-themed Node Graph example using PySide6 and NodeGraphQt.
Includes a main menu bar, dark blue nodes, a properly registered 'Run' button,
and an 'Add Node' option in the right-click context menu.
"""
import os
from re import S

from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar
from PySide6.QtGui import QAction, QCursor
from NodeGraphQt import NodeGraph, BaseNode, NodesMenu

# ----------------------------------------------------------------------
# Custom Node Definition
# ----------------------------------------------------------------------
class MyNode(BaseNode):
    """
    Custom dark-blue node with input/output ports and a 'Run' button.
    """
    __identifier__ = 'com.flowdip'
    NODE_NAME = 'FlowDip Node'

    def __init__(self):
        super(MyNode, self).__init__()

        # Dark, bluish tone for node body
        self.set_color(25, 35, 55)  # Almost black, slight blue tint
        # Add ports
        self.add_input('Input')
        self.add_output('Output')

        # Add a registered Run button
        self.add_button(name='btn_run', text='Run')
        btn = self.get_widget('btn_run')
        btn._button.setStyleSheet(STYLESHEET)  # Apply custom stylesheet to button
        # btn.pressed.connect(self.on_run_pressed)
        btn.setToolTip('Execute this node')
        btn._button.clicked.connect(self.on_run_pressed)

    # ------------------------------------------------------------------
    def on_run_pressed(self):
        """Callback executed when the Run button is clicked."""
        print(f"Node '{self.name()}' executed!")


# ----------------------------------------------------------------------
# Main Application Window
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize node graph
        self.graph = NodeGraph()
        self.viewer = self.graph.widget
        self.viewer.setStyleSheet(STYLESHEET)  # Apply custom stylesheet to viewer
        self.graph.get_context_menu("graph").qmenu.setStyleSheet(STYLESHEET)
        self.graph.get_context_menu("nodes").qmenu.setStyleSheet(STYLESHEET)

        # Register custom node type
        self.graph.register_node(MyNode)

        # Create a sample node
        self.graph.create_node('com.flowdip.MyNode', name='Node A', pos=(100, 100))

        # Extend the built-in context menu
        self._extend_context_menu()

        # Apply dark, desaturated theme
        self.graph.set_background_color(15, 17, 22)  # Deep charcoal gray
        self.graph.set_grid_color(40, 45, 60)        # Muted bluish grid

        # Basic window setup
        self.setWindowTitle("FlowDip - Node Graph (Dark Blue Theme)")
        self.resize(900, 700)
        self.setCentralWidget(self.viewer)

        # Add menu bar
        self._create_menus()

    # ------------------------------------------------------------------
    # Extend NodeGraphQt Context Menu
    # ------------------------------------------------------------------
    def _extend_context_menu(self):
        """
        Adds an 'Add Node' option to the background right-click context menu.
        """
        menu = self.graph.context_menu()
        menu.add_separator()
        menu.add_command(
            name="Add Node",
            func=self._on_add_node,
        )

    # ------------------------------------------------------------------
    # Add Node Command
    # ------------------------------------------------------------------
    def _on_add_node(self):
        """
        Adds a new MyNode instance at the current cursor (mouse) position.
        """
        viewer = self.graph.viewer()
        cursor_pos = QCursor.pos()  # Global cursor position
        local_pos = viewer.mapFromGlobal(cursor_pos)
        scene_pos = viewer.mapToScene(local_pos)

        self.graph.create_node(
            'com.flowdip.MyNode',
            name='New Node',
            pos=(scene_pos.x(), scene_pos.y())
        )

        print(f"New node added at ({scene_pos.x():.0f}, {scene_pos.y():.0f})")

    # ------------------------------------------------------------------
    # Menu Bar
    # ------------------------------------------------------------------
    def _create_menus(self):
        menu_bar = QMenuBar(self)

        # File Menu
        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_graph)
        file_menu.addAction(new_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_graph)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")

        clear_action = QAction("Clear Graph", self)
        clear_action.triggered.connect(self.clear_graph)
        edit_menu.addAction(clear_action)

        menu_bar.setNativeMenuBar(False)
        self.setMenuBar(menu_bar)

    # ------------------------------------------------------------------
    # Menu Actions
    # ------------------------------------------------------------------
    def new_graph(self):
        """Clear and start a new graph."""
        self.graph.clear_session()
        print("🧩 New graph created.")

    def save_graph(self):
        """Placeholder for saving."""
        print("💾 Save graph (not implemented).")

    def clear_graph(self):
        """Remove all nodes."""
        self.graph.clear_graph()
        print("🧹 Graph cleared.")

STYLESHEET = ""
# ----------------------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------------------
def main():
    app = QApplication([])

    # Load external stylesheet (CSS/QSS)
    css_path = os.path.join(os.path.dirname(__file__), "themes/dark_blue.css")

    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            STYLESHEET = f.read()
            app.setStyleSheet(STYLESHEET)
        print(f"Loaded stylesheet: {css_path}")
    else:
        print(f"Stylesheet not found: {css_path}")

    # Create and show the main window
    window = MainWindow()
    window.setStyleSheet(STYLESHEET)  # Apply stylesheet to main window
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
