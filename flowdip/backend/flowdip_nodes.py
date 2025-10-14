from time import sleep
import cv2
import numpy as np
from multiprocessing.shared_memory import SharedMemory

from flowdip import Event, EventType, UpdateNodeParamsPayload
from flowdip.backend.flowdip_be_base import BackEndFlowDiPNode
import os

class BackMediaPlayer(BackEndFlowDiPNode):

    _loop = True

    def __init__(self, flowdip_name, be_manager=None):
        super().__init__(flowdip_name=flowdip_name, be_manager=be_manager)

        self.videopath = None
        self.cap =  None
        self.shm = None
        self.frame_shape = None
        self.frame_size = None
        self.frame_dtype = None

    def open_video_cap_from_file(self, videopath):

        if not videopath:
            raise ValueError("videopath is not set. Please set a valid videopath before updating.")

        if not os.path.isfile(videopath):
            raise ValueError(f"Failed to open video file at '{self.videopath}'. Please check the file and try again.")

        self.cap = cv2.VideoCapture(videopath)

        if not self.cap.isOpened():
            raise ValueError(f"Failed to open video file at '{self.videopath}'. Please check the file and try again.")

        self.videopath = videopath

        ret, frame = self.cap.read()

        frame_shape = frame.shape
        frame_dtype = frame.dtype

        if frame_shape != self.frame_shape or frame_dtype != self.frame_dtype:

            self.frame_shape = frame_shape
            self.frame_dtype = frame_dtype
            self.frame_size = np.prod(self.frame_shape) * np.dtype(self.frame_dtype).itemsize
            # If there was a previous shared memory block, release it
            if self.shm is not None:
                self.shm.close()
                self.shm.unlink()
                self.logger.info(f"Released previous shared memory block for node {self.flowdip_name()}")

            # Create fresh new shared memory block
            self.shm = SharedMemory(name=self.flowdip_name, create=True, size=self.frame_size)

            self.update_frontend_shared_memory()

    def _process_data(self):
        if self.cap is None or not self.cap.isOpened():
            if self.videopath:
                self.open_video_cap_from_file(self.videopath)
            else:
                raise ValueError("VideoCapture is not opened. Please set a valid videopath before processing data.")

        ret, frame = self.cap.read()
        sleep(0.016)  # Simulate processing time
        # Write frame to shared memory
        np_frame = np.ndarray(self.frame_shape, dtype=self.frame_dtype, buffer=self.shm.buf)
        np.copyto(np_frame, frame)

        # Tell frontend node to update frame
        self.be_manager.publish_event(
            Event(
                event_type=EventType.UPDATE_NODE_PARAMS,
                payload=UpdateNodeParamsPayload(
                    flowdip_name=self.flowdip_name,
                    new_params={}
                )
            )
        )

    def update_frontend_shared_memory(self):
        self.be_manager.publish_event(
            Event(
                event_type=EventType.UPDATE_NODE_PARAMS,
                payload=UpdateNodeParamsPayload(
                    flowdip_name=self.flowdip_name,
                    new_params={
                    "shm_name": self.shm.name,
                    "shm_shape": self.frame_shape,
                    "shm_dtype": self.frame_dtype
                    }
                )
            )
        )

    def update_params(self, params: dict):
        videopath = params.get('videopath', None)
        if videopath is not None:
            self.open_video_cap_from_file(videopath)
            self.start_e.set()



