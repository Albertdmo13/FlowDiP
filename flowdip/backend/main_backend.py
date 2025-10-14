import logging
from threading import Thread
from multiprocessing import Queue
from flowdip import Request, RequestType
from typing import Set
from flowdip.backend.flowdip_be_base import BackEndFlowDiPNode

# ----------------------------------------------------------------------
# Logger configuration
# ----------------------------------------------------------------------
logger = logging.getLogger("Backend Manager")
logger.setLevel(logging.DEBUG)  # You can adjust this to INFO, WARNING, etc.

# Add a handler with formatting if it does not already exist
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

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
        self.nodes: Set[BackEndFlowDiPNode] = set()
        self.logger = logger  # Use the global logger defined above

    def run(self):
        self.logger.info("Backend Manager started.")
        while self._running:
            req = self.req_queue.get()
            self.logger.debug(f"Received request: {req}")
            if req.request_type == RequestType.SHUTDOWN:
                self.logger.info("Shutdown request received. Stopping manager.")
                self._running = False
            else:
                self.handle_request(req)
        self.logger.info("Backend Manager stopped.")

    def handle_request(self, request: Request):
        req_type = request.request_type
        req_payload = request.payload
        self.logger.debug(f"Handling request type: {req_type}, payload: {req_payload}")

        if req_type == RequestType.CREATE_NODE:
            self.create_node(req_payload)

        if req_type == RequestType.UPDATE_NODE_PARAMS:
            for node in self.nodes:
                if node.flowdip_name == req_payload.flowdip_name:
                    node.update_params(req_payload.new_params)
                    self.logger.info(f"Node parameters updated: {node}")
                    break

    def create_node(self, req_payload):
        # Unpack payload
        node_class_name = req_payload.node_class_name
        flowdip_name = req_payload.flowdip_name
        loop = req_payload.loop
        other_params = req_payload.other_params if req_payload.other_params else {}

        self.logger.info(f"Creating node: class={node_class_name}, name={flowdip_name}")

        node_class = None
        for cls in BackEndFlowDiPNode.__subclasses__():
            if cls.__name__ == node_class_name:
                node_class = cls
                new_node = node_class(flowdip_name=flowdip_name, loop=loop, **other_params, be_manager=self)
                self.nodes.add(new_node)
                self.logger.info(f"Node created and added: {new_node}")
                break

        if node_class is None:
            self.logger.error(f"Node class '{node_class_name}' not found among Base Node subclasses.")

    def delete_node(self, req_payload):
        flowdip_name = req_payload.flowdip_name

        self.logger.info(f"Deleting node: name={flowdip_name}")

        # Find and remove the node from the set
        node_to_remove = None
        for node in self.nodes:
            if node.flowdip_name == flowdip_name:
                node_to_remove = node
                break

        if node_to_remove:
            self.nodes.remove(node_to_remove)
            self.logger.info(f"Node deleted: {node_to_remove}")
        else:
            self.logger.warning(f"Node not found for deletion: {flowdip_name}")

def main(request_queue, response_queue):
    be_manager = BackEndManager(request_queue, response_queue)
    be_manager.start()
    be_manager.join()
