__author__ = 'hungtantran'

from logger import Logger
from logger import LogLevel
from models import ServiceQuery

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

class ThriftIndexClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __enter__(self):
        # Make socket
        self.transport = TSocket.TSocket('localhost', 9090)

        # Buffering is critical. Raw sockets are very slow
        self.transport = TTransport.TBufferedTransport(self.transport)

        # Wrap in a protocol
        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        # Create a client to use the protocol encoder
        self.client = ServiceQuery.Client(self.protocol)

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
        Logger.log(LogLevel.INFO, 'Client exit with type %s, val %s, traceback %s' % (
            exc_type, exc_val, exc_tb))
        self.transport.close()
