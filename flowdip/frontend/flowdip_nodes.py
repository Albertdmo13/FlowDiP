from typing import Optional
from flowdip.frontend.qtwidgets.ui_local_media_player import LocalMediaPlayerWidget
from flowdip.backend.flowdip_nodes import BackMediaPlayer
from flowdip.frontend.flowdip_fe_base import FrontFlowDiPNode

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
