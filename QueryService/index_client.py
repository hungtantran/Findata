__author__ = 'hungtantran'

from logger import Logger
from logger import LogLevel
from thrift_index_client import ThriftIndexClient

def main():
    with ThriftIndexClient('localhost', 9090) as client:
        client.ping()
        print(client.get_service_name())
        print(client.get_indices())

if __name__ == '__main__':
    try:
        main()
    except Exception as tx:
        LogLevel.log(LogLevel.ERROR, tx)