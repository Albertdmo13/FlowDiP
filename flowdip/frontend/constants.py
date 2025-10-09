import os
import flowdip

# ----------------------------------------------------------------------
# Global Constants
# ----------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(flowdip.__file__))
MENU_JSON_PATH = os.path.join(BASE_DIR, "frontend/hotkeys/hotkeys.json")
THEMES_DIR = os.path.join(BASE_DIR, "frontend/themes")

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
