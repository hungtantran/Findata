__author__ = 'hungtantran'

from models import ServiceQuery

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class ThriftIndexServer(object):
    def __init__(self, host, port, handler):
        self.host = host
        self.port = port
        self.handler = handler

    def __enter__(self):
        processor = ServiceQuery.Processor(self.handler)
        transport = TSocket.TServerSocket(host=self.host, port=self.port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        self.server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

        return self

    def serve(self):
        self.server.serve()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Server exit with type %s, val %s, traceback %s' % (
            exc_type, exc_val, exc_tb))