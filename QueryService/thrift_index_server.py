__author__ = 'hungtantran'


import threading

import logger
import models.ServiceQuery

import thrift.transport.TSocket
import thrift.transport.TTransport
import thrift.protocol.TBinaryProtocol
import thrift.server.TServer


class ThriftIndexServer(object):
    def __init__(self, host, port, handler):
        logger.Logger.log(
            logger.LogLevel.INFO,
            'Start index server %s at %s:%s' % (handler.get_service_name(), host, port))
        self.host = host
        self.port = port
        self.handler = handler

    def __enter__(self):
        processor = models.ServiceQuery.Processor(self.handler)
        transport = thrift.transport.TSocket.TServerSocket(host=self.host, port=self.port)
        tfactory = thrift.transport.TTransport.TBufferedTransportFactory()
        pfactory = thrift.protocol.TBinaryProtocol.TBinaryProtocolFactory()

        self.server = thrift.server.TServer.TSimpleServer(processor, transport, tfactory, pfactory)

        return self

    def serve(self):
        self.server.serve()

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.Logger.log(logger.LogLevel.INFO, 'Server exit with type %s, val %s, traceback %s' % (
            exc_type, exc_val, exc_tb))


class RPCIndexServer(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.handler = handler

    def run(self):
        with ThriftIndexServer('localhost', 9090, self.handler) as server:
            server.serve()