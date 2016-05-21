__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from dao_factory_repo import DAOFactoryRepository
from sec_ticker_info_helper import SecTickerInfoHelper


def find_rogue_table():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute('SHOW TABLES')
            data = cursor.fetchall()
            tables = []
            for row in data:
                tables.append(row[0])

            cursor.execute('select tablename from data_source')
            data = cursor.fetchall()
            table_registered = []
            for row in data:
                table_registered.append(row[0])

            rogue_table = [table for table in tables if table not in table_registered]
            print rogue_table
            return rogue_table
        except Exception as e:
            print e

def find_nonexisting_table():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute('SHOW TABLES')
            data = cursor.fetchall()
            tables = []
            for row in data:
                tables.append(row[0])

            cursor.execute('select tablename from data_source')
            data = cursor.fetchall()
            table_registered = []
            for row in data:
                table_registered.append(row[0])

            nonexisting_table = [table for table in table_registered if table not in tables]
            print nonexisting_table
            return nonexisting_table
        except Exception as e:
            print e


#find_nonexisting_table()
#find_rogue_table()


