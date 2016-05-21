__author__ = 'hungtantran'


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
            cursor.execute('SHOW TABLES LIKE "%\_metrics"')
            data = cursor.fetchall()
            for row in data:
                try:
                    original_name = row[0]
                    name = 'company_fundamentals_' + original_name
                    name = name.lower()
                    print 'Update %s to %s' % (original_name, name)
                    cursor2 = connection.cursor()
                    cursor2.execute('RENAME TABLE %s to %s' %(original_name, name))
                    connection.commit()
                except Exception as e:
                    print e

        except Exception as e:
            print e


if __name__ == '__main__':
    #rename_table()


