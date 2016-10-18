__author__ = 'hungtantran'


import init_app
import filecmp
import os
import unittest

import logger
from constants_config import Config
from dao_factory_repo import DAOFactoryRepository
from sec_ticker_info_helper import SecTickerInfoHelper


def rename_table():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute('SHOW TABLES LIKE "%economics\_info\_%"')
            data = cursor.fetchall()
            for row in data:
                try:
                    original_name = row[0]
                    name = original_name + '_metrics'
                    name = name.lower()
                    print 'Update %s to %s' % (original_name, name)
                    cursor2 = connection.cursor()
                    cursor2.execute('RENAME TABLE %s to %s' %(original_name, name))
                    connection.commit()
                except Exception as e:
                    print e

        except Exception as e:
            print e

def rename_ticker_info_table():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM ticker_info')
            data = cursor.fetchall()
            for row in data:
                try:
                    id = row[0]
                    ticker = row[1]

                    original_name = ticker.lower() + '_metrics'
                    new_name = 'ticker_info_' + str(id) + '_metrics'
                    print 'Update %s to %s' % (original_name, new_name)
                    cursor2 = connection.cursor()
                    cursor2.execute('RENAME TABLE %s to %s' %(original_name, new_name))
                    connection.commit()
                except Exception as e:
                    print e

        except Exception as e:
            print e    


if __name__ == '__main__':
    #rename_table()
    rename_ticker_info_table();
    pass
