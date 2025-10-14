from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication
from multiprocessing import Queue
from flowdip import Event, EventType, Request, RequestType
from flowdip.frontend.constants import GLOBAL_STYLESHEET
from flowdip.frontend.mainwindow import MainWindow
from flowdip.frontend.flowdip_fe_base import FlowDiPNodeGraph

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
        self.graph = None  # type: FlowDiPNodeGraph

    def run(self):
        while self._running:
            ev = self.event_queue.get()
            if ev.event_type == EventType.SHUTDOWN:
                self._running = False
            else:
                self.handle_event(ev)

    def publish_request(self, req: Request):
        self.req_queue.put(req)

    def handle_event(self, ev: Event):

        if ev.event_type == EventType.UPDATE_NODE_PARAMS:
            # Handle node parameter updates if needed
            for node in self.graph.all_nodes():
                if node.flowdip_name == ev.payload.flowdip_name:
                    node.update_params(ev.payload.new_params)
                    break

# ----------------------------------------------------------------------
# Application Entry Point
# ----------------------------------------------------------------------
def main(request_queue, response_queue):

    app = QApplication([])

    # Load CSS stylesheet
    if GLOBAL_STYLESHEET is not None:
        app.setStyleSheet(GLOBAL_STYLESHEET)

        # Create frontend manager thread
    fe_manager = FrontEndManager(request_queue, response_queue)
    window = MainWindow(fe_manager)

    fe_manager.graph = window.graph

    fe_manager.start()

    # Launch main window
    if GLOBAL_STYLESHEET:
        window.setStyleSheet(GLOBAL_STYLESHEET)
    window.show()

    app.exec()

    fe_manager._running = False
    fe_manager.event_queue.put(Event(event_type=EventType.SHUTDOWN, payload=None))
    fe_manager.req_queue.put(Request(request_type=RequestType.SHUTDOWN, payload=None))

    fe_manager.wait()
