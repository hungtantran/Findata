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

#write_query_to_file("show tables like '%\_metrics%'", 'tables.txt')
#execute_query("INSERT IGNORE INTO ticker_info (ticker) VALUES ('AAMC')")