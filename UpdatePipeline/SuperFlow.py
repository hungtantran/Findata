__author__ = 'hungtantran'

import init_app

import time

import logger
from UpdatePipeline.Flow import Flow
from UpdatePipeline.Flow import FlowStatus


class SuperFlow(Flow):
    SUBFLOW_POLLING_PERIOD_IN_SECS = 5
    subflows = None

    def __init__(self, flow_name):
        super(SuperFlow, self).__init__(flow_name)
        self.subflows = []

    def debug_string(self):
        debug_str = 'Flow %s (status %s) has %d subflows:\n' % (self.flow_name, self.status(), len(self.subflows))
        for subflow in self.subflows:
            debug_str += '%s\n' % subflow.debug_string()
        return debug_str

    def start(self):
        self.status = FlowStatus.STARTED
        for subflow in self.subflows:
            try:
                subflow.start()
                while True:
                    status = subflow.status()

                    if status == FlowStatus.SUCCESS:
                        break

                    if status == FlowStatus.STARTED:
                        time.sleep(SuperFlow.SUBFLOW_POLLING_PERIOD_IN_SECS)
                        continue

                    logger.Logger.error('Subflow fail %s with status %s' % (subflow.debug_string(), subflow.status()))
                    self.status = FlowStatus.ERROR
                    return
            except Exception as e:
                self.status = FlowStatus.ERROR
                logger.Logger.error(e)
                raise e
        self.status = FlowStatus.SUCCESS

    def rollback(self):
        raise NotImplementedError

    def add_subflow(self, subflow):
        self.subflows.append(subflow)