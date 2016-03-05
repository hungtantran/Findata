__author__ = 'hungtantran'

from models import ServiceQuery

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


class BloombergHandler:
    def __init__(self):
        self.log = {}

    def ping(self):
        print('ping()')

    def get_service_name(self):
        return 'Bloomberg_Service'

    def get_indices(self):
        return ["a", "b"]


if __name__ == '__main__':
    handler = BloombergHandler()
    processor = ServiceQuery.Processor(handler)
    transport = TSocket.TServerSocket(host='localhost',port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server.serve()