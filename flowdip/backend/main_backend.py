from threading import Thread
from multiprocessing import Queue
from flowdip import Request, RequestType

# ----------------------------------------------------------------------
# Back End Manager
# ----------------------------------------------------------------------

class BackEndManager(Thread):
    """Handles the backend request queue."""

    def __init__(self, req_queue: Queue, event_queue: Queue):
        super().__init__()
        self.req_queue = req_queue
        self.event_queue = event_queue
        self._running = True

    def run(self):
        while self._running:
            req = self.req_queue.get()
            if req.request_type == RequestType.SHUTDOWN:
                self._running = False
            else:
                self.handle_request(req)

    def handle_request(self, request: Request):
        pass

def main(request_queue, response_queue):
    be_manager = BackEndManager(request_queue, response_queue)
    be_manager.start()
    be_manager.join()
