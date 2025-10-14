import cv2
import numpy as np
from multiprocessing.shared_memory import SharedMemory

from typing import Optional
from flowdip.frontend.qtwidgets.ui_local_media_player import LocalMediaPlayerWidget
from flowdip.backend.flowdip_nodes import BackMediaPlayer
from flowdip.frontend.flowdip_fe_base import FrontFlowDiPNode
from flowdip import Request, RequestType, UpdateNodeParamsPayload
# =============================================================================
#  Specific nodes
# =============================================================================

class FrontMediaPlayer(FrontFlowDiPNode):

    NODE_NAME = "Media Player"

    widget_class = LocalMediaPlayerWidget
    be_node_class = BackMediaPlayer
    loop = True

    def __init__(self):
        super().__init__()
        self.add_output("Frame")
        self.add_output("Sound")

        self.frame_shape: Optional[tuple] = None
        self.frame_dtype: Optional[str] = None
        self.shm_name: Optional[str] = None
        self.shm = None
        self.shared_frame = None

    def update_videopath(self, videopath: str):
        """Update the videopath in the backend node."""
        if self.fe_manager and self.be_node_class:
            self.fe_manager.publish_request(
                Request(
                    request_type=RequestType.UPDATE_NODE_PARAMS,
                    payload=UpdateNodeParamsPayload(
                        flowdip_name=self.flowdip_name,
                        new_params={"videopath": videopath}
                    )
                )
            )

    def update_params(self, new_params: dict):
        """Update node parameters."""
        if "shm_name" in new_params.keys():
            """Update shared memory parameters event"""
            self.logger.info(f"Updating shared memory parameters for node {self.name()}")
            self.shm_name = new_params.get("shm_name", self.shm_name)
            self.frame_shape = new_params.get("shm_shape", self.frame_shape)
            self.frame_dtype = new_params.get("shm_dtype", self.frame_dtype)
            if self.shm is None and self.shm_name and self.frame_shape and self.frame_dtype:
                self.shm = SharedMemory(name=self.shm_name)
                self.logger.info(f"Attached to shared memory block {self.shm_name} for node {self.name()}")
                self.shared_frame = np.ndarray(self.frame_shape, dtype=self.frame_dtype, buffer=self.shm.buf)
        else:
            # Update frame event
            #self.logger.info(f"Received frame update for node {self.name()}")
            #if self.shared_frame is not None:
            #    self.logger.debug(f"Output frame updated for node {self.name()}")
            #else:
            #    self.logger.warning(f"Shared frame is not set for node {self.name()}. Cannot update output.")
            self.embedded_widget.video_display.update_frame()
            self.embedded_widget.update()

