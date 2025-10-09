from typing import Optional
from flowdip.frontend.qtwidgets.ui_local_media_player import LocalMediaPlayerWidget
from flowdip.backend.flowdip_be_base import BackEndFlowDiPNode
from flowdip.frontend.flowdip_fe_base import FrontEndFlowDiPNode

# =============================================================================
#  Specific nodes
# =============================================================================


class MediaPlayer(FrontEndFlowDiPNode):
    __identifier__ = "com.flowdip"
    NODE_NAME = "Media Player"

    widget_class = LocalMediaPlayerWidget
    be_node_class = BackEndFlowDiPNode

    def __init__(self):
        super().__init__(self.widget_class, self.be_node_class)

        self.add_output("Frame")
        self.add_output("Sound")
