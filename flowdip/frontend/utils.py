from flowdip.frontend.constants import GLOBAL_STYLESHEET
from NodeGraphQt import NodeGraphMenu

# Helper to recursively set stylesheets for context menus
def set_context_menu_stylesheet(menu):
    if isinstance(menu, NodeGraphMenu):
        menu.qmenu.setStyleSheet(GLOBAL_STYLESHEET)
        for item in menu.get_items():
            set_context_menu_stylesheet(item)
