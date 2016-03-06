__author__ = 'hungtantran'

import threading

from models import ServiceQuery

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class ThriftIndexServer(object):
    def __init__(self, host, port, handler):
        print('Start index server %s at %s:%s' % (handler.get_service_name(), host, port))
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


class RPCIndexServer(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.handler = handler

    def run(self):
        with ThriftIndexServer('localhost', 9090, self.handler) as server:
            server.serve()