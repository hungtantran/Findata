__author__ = 'hungtantran'

from models import ServiceQuery
from thrift_index_server import ThriftIndexServer

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


def main():
    handler = BloombergHandler()
    with ThriftIndexServer('localhost', 9090, handler) as server:
        server.serve()


if __name__ == '__main__':
    try:
        main()
    except Exception as tx:
        print(tx)