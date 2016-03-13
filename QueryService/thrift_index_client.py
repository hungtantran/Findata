__author__ = 'hungtantran'


import logger
import models.ServiceQuery

import thrift.transport.TSocket
import thrift.transport.TTransport
import thrift.protocol.TBinaryProtocol


class ThriftIndexClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        # Make socket
        self.transport = thrift.transport.TSocket.TSocket('localhost', 9090)

        # Buffering is critical. Raw sockets are very slow
        self.transport = thrift.transport.TTransport.TBufferedTransport(self.transport)

        # Wrap in a protocol
        self.protocol = thrift.protocol.TBinaryProtocol.TBinaryProtocol(self.transport)

        # Create a client to use the protocol encoder
        self.client = models.ServiceQuery.Client(self.protocol)

        # Connect!
        self.transport.open()

        return self

    def ping(self):
        return self.client.ping()

    def get_service_name(self):
        return self.client.get_service_name()

    def get_indices(self):
        return self.client.get_indices()

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.Logger.log(logger.LogLevel.INFO, 'Client exit with type %s, val %s, traceback %s' % (
            exc_type, exc_val, exc_tb))
        self.transport.close()
