__author__ = 'hungtantran'

import init_app


class FlowStatus(object):
    UNKNOWN = 0
    NOT_START = 1
    STARTED = 2
    ERROR = 3
    SUCCESS = 4


class Flow(object):
    flow_name = None
    status = FlowStatus.UNKNOWN

    def __init__(self, flow_name):
        self.flow_name = flow_name
        self.status = FlowStatus.NOT_START

    def debug_string(self):
        debug_str = 'Flow %s (status %s)' % (self.flow_name, self.status())
        return debug_str

    def status(self):
        return self.status

    def start(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError
