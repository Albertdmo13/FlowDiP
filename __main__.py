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

from flowdip.frontend.hotkeys.hotkey_functions import *  # if needed
import flowdip.frontend.flowdip_nodes as flowdip_nodes


from multiprocessing import Process, Queue

from __init__ import *  # to load themes and global constants

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

