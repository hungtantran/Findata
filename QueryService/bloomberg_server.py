__author__ = 'hungtantran'

import threading

from models import ServiceQuery
from thrift_index_server import ThriftIndexServer
from thrift_index_server import RPCIndexServer

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
    try:
        handler = BloombergHandler()
        bloomberg_rpc_server = RPCIndexServer(handler)
        bloomberg_rpc_server.start()
        bloomberg_rpc_server.join()
    except Exception as tx:
        print(tx)