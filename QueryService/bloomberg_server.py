__author__ = 'hungtantran'

import threading

from logger import Logger
from logger import LogLevel
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


def start_bloomberg_server():
    handler = BloombergHandler()
    bloomberg_rpc_server = RPCIndexServer(handler)
    bloomberg_rpc_server.start()
    return bloomberg_rpc_server

if __name__ == '__main__':
    threads = []

    try:
        threads.append(start_bloomberg_server())
    except Exception as tx:
        print(tx)

    Logger.log(LogLevel.INFO, 'Server starts waiting for all threads to finish')
    for thread in threads:
        thread.join()
    Logger.log(LogLevel.INFO, 'Server exits')