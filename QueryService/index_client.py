__author__ = 'hungtantran'


import logger
import thrift_index_client


def main():
    with thrift_index_client.ThriftIndexClient('localhost', 9090) as client:
        client.ping()
        print(client.get_service_name())
        print(client.get_indices())


if __name__ == '__main__':
    try:
        main()
    except Exception as tx:
        logger.Logger.log(logger.LogLevel.ERROR, tx)