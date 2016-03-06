__author__ = 'hungtantran'

from thrift_index_client import ThriftIndexClient

def main():
    # Make socket
    with ThriftIndexClient('localhost', 9090) as client:
        client.ping()
        print(client.get_service_name())
        print(client.get_indices())

if __name__ == '__main__':
    try:
        main()
    except Exception as tx:
        print(tx)