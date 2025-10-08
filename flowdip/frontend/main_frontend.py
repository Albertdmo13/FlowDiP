import os

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
    "node_bg": (40, 45, 57),         # Darker node body
    "node_border": (65, 80, 100),    # Darker node border
    "accent": (100, 140, 210),       # Muted accent
    "text": (210, 220, 235),         # Softer text
    "css": os.path.join(THEMES_DIR, "dark_blue.css"),
    "node_running" : (70, 130, 180),  # Steel blue for running state
    "node_error" : (220, 20, 60),     # Crimson for error state
}

# Set active theme
ACTIVE_THEME = DARK_BLUE

# ----------------------------------------------------------------------
# Global stylesheet (loaded at runtime)
# ----------------------------------------------------------------------
GLOBAL_STYLESHEET = ""

# Load CSS stylesheet
css_path = ACTIVE_THEME["css"]
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        GLOBAL_STYLESHEET = f.read()


# Helper to recursively set stylesheets for context menus
def set_context_menu_stylesheet(menu):
    if isinstance(menu, NodeGraphMenu):
        menu.qmenu.setStyleSheet(GLOBAL_STYLESHEET)
        for item in menu.get_items():
            set_context_menu_stylesheet(item)

# ----------------------------------------------------------------------
# Front End Manager
# ----------------------------------------------------------------------

class FrontEndManager(QThread):
    """Handles frontend events."""

    def __init__(self, req_queue: Queue, event_queue: Queue):
        super().__init__()
        self.req_queue = req_queue
        self.event_queue = event_queue
        self._running = True

    def run(self):
        while self._running:
            ev = self.event_queue.get()
            if ev.event_type == EventType.SHUTDOWN:
                self._running = False
            else:
                self.handle_event(ev)

    def handle_event(self, ev: Event):
        pass


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
    fe_manager = FrontEndManager(request_queue, response_queue)
    fe_manager.start()

    # Launch main window
    window = MainWindow(fe_manager)
    if GLOBAL_STYLESHEET:
        window.setStyleSheet(GLOBAL_STYLESHEET)
    window.show()

    app.exec()

    fe_manager._running = False
    fe_manager.event_queue.put(flowdip_nodes.Event(event_type=flowdip_nodes.EventType.SHUTDOWN, payload=None))
    fe_manager.req_queue.put(flowdip_nodes.Request(request_type=flowdip_nodes.RequestType.SHUTDOWN, payload=None))

    fe_manager.wait()