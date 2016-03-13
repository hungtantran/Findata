__author__ = 'hungtantran'


import threading

import logger
import thrift_index_server


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
    bloomberg_rpc_server = thrift_index_server.RPCIndexServer(handler)
    bloomberg_rpc_server.start()
    return bloomberg_rpc_server


if __name__ == '__main__':
    threads = []

    try:
        threads.append(start_bloomberg_server())
    except Exception as tx:
        print(tx)

    logger.Logger.log(logger.LogLevel.INFO, 'Server starts waiting for all threads to finish')
    for thread in threads:
        thread.join()
    logger.Logger.log(logger.LogLevel.INFO, 'Server exits')