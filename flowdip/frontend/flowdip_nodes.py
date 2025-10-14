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