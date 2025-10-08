from typing import List, Optional, Any
from enum import IntEnum, Enum
from dataclasses import dataclass
from threading import Thread, Event
from multiprocessing import Queue
from PySide6.QtCore import QMetaObject, Qt, QThread
from PySide6.QtWidgets import QSizePolicy
from NodeGraphQt import BaseNode, Port, NodeBaseWidget
from qtwidgets.ui_local_media_player import LocalMediaPlayerWidget
from data_classes import Dataset

# Import global constants and themes
from __init__ import *  # noqa

# =============================================================================
#  Specific nodes
# =============================================================================

class DatasetGenerator(FrontEndFlowDiPNode):
    NODE_NAME = "Dataset Generator"

    def __init__(self):
        super().__init__()
        self.dataset: Optional[Dataset] = None

class MediaPlayer(FrontEndFlowDiPNode):
    __identifier__ = "com.flowdip"
    NODE_NAME = "Media Player"

    widget_class = LocalMediaPlayerWidget
    be_node_class = BackEndFlowDiPNode

    def __init__(self):
        super().__init__(self.widget_class, self.be_node_class)

        self.add_output("Frame")
        self.add_output("Sound")
