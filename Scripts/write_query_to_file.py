__author__ = 'hungtantran'


import datetime
import re
from time import sleep

import logger
from dao_factory_repo import DAOFactoryRepository
from string_helper import StringHelper
from constants_config import Config


def write_query_to_file(query, file):
    if ('delete' in query.lower()) or ('insert' in query.lower()) or ('update' in query.lower()):
        print 'Cant execute modify query'
        return

    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            data_str_arr = []
            for row in data:
                data_str = ''
                for cell in row:
                    data_str += str(cell) + ','
                data_str_arr.append(data_str)

            with open(file, 'w') as f:
                f.write('\n'.join(data_str_arr))
        except Exception as e:
            print e

def execute_query(query):
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
        except Exception as e:
            print e

if __name__ == '__main__':
    #write_query_to_file("show tables like '%\_metrics%'", 'tables.txt')
    #write_query_to_file("select * from msft_metrics", 'metrics.txt')
    #write_query_to_file("select * from exchange_stockprice_msft_adj_close", 'adj_close.txt')
    #write_query_to_file("select * from exchange_stockprice_msft_volume", 'volume.txt')
    #write_query_to_file("select * from company_fundamentals_msft_metrics", 'fundamentals.txt')
    #write_query_to_file("show tables like 'a%\_metrics'", 'tables.txt')
    #write_query_to_file("show tables where tables_in_models like 'exchange_stockprice%' and tables_in_models > ' exchange_stockprice_' and tables_in_models < 'exchange_stockprice_inn'", 'exchange_stockprice.txt')
    #write_query_to_file("select lower(ticker) from ticker_info where ticker REGEXP '^[A-Za-z0-9]+$'", 'metric_tables.txt')
    write_query_to_file("select count(*) as num, name from ticker_info group by name order by num desc", 'ticker_name_and_count.txt')