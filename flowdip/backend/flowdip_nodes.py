from flowdip.backend.flowdip_be_base import BackEndFlowDiPNode

class BackMediaPlayer(BackEndFlowDiPNode):
    def __init__(self, flowdip_name, loop=False):
        super().__init__(flowdip_name=flowdip_name, loop=loop)