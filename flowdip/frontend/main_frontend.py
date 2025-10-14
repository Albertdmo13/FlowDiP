from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication
from multiprocessing import Queue
from flowdip import Event, EventType, Request, RequestType
from flowdip.frontend.constants import GLOBAL_STYLESHEET
from flowdip.frontend.mainwindow import MainWindow
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
        self.nodes = []

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
            for node in MainWindow.all_nodes:
                if node.flowdip_name == ev.payload["flowdip_name"]:
                    node.update_shared_memory(ev.payload["shm_name"],
                                              ev.payload["shm_shape"],
                                              ev.payload["shm_dtype"])
                    break
        pass

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
    fe_manager.start()

    # Launch main window
    window = MainWindow(fe_manager)
    if GLOBAL_STYLESHEET:
        window.setStyleSheet(GLOBAL_STYLESHEET)
    window.show()

    app.exec()

    fe_manager._running = False
    fe_manager.event_queue.put(Event(event_type=EventType.SHUTDOWN, payload=None))
    fe_manager.req_queue.put(Request(request_type=RequestType.SHUTDOWN, payload=None))

    fe_manager.wait()
