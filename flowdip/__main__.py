# -*- coding: utf-8 -*-
"""
FlowDip — Node Graph editor using PySide6 + NodeGraphQt.
"""
from multiprocessing import Process, Queue

from flowdip.backend.main_backend import main as main_backend
from flowdip.frontend.main_frontend import main as main_frontend

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

