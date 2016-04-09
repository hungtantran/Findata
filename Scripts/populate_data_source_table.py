__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from dao_factory_repo import DAOFactoryRepository
from sec_ticker_info_helper import SecTickerInfoHelper
import validate_database


def populate_data_source_with_ticker_info():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute('SELECT ticker from ticker_info')
            data = cursor.fetchall()
            val_arr = []
            index = 0
            for row in data:
                index += 1
                try:
                    ticker = row[0].lower()
                    if not ticker.isalnum():
                        continue

                    cursor2 = connection.cursor()
                    name = ticker + '_adj_close'
                    tablename = 'exchange_stockprice_' + name
                    val_arr.append("('%s', '%s', '%s', '%s', '%s', '%s')" % ('exchange', 'stockprice', 'us', name, tablename, 'timeseries'))

                    name = ticker + '_close'
                    tablename = 'exchange_stockprice_' + name
                    val_arr.append("('%s', '%s', '%s', '%s', '%s', '%s')" % ('exchange', 'stockprice', 'us', name, tablename, 'timeseries'))

                    name = ticker + '_open'
                    tablename = 'exchange_stockprice_' + name
                    val_arr.append("('%s', '%s', '%s', '%s', '%s', '%s')" % ('exchange', 'stockprice', 'us', name, tablename, 'timeseries'))

                    name = ticker + '_high'
                    tablename = 'exchange_stockprice_' + name
                    val_arr.append("('%s', '%s', '%s', '%s', '%s', '%s')" % ('exchange', 'stockprice', 'us', name, tablename, 'timeseries'))

                    name = ticker + '_low'
                    tablename = 'exchange_stockprice_' + name
                    val_arr.append("('%s', '%s', '%s', '%s', '%s', '%s')" % ('exchange', 'stockprice', 'us', name, tablename, 'timeseries'))

                    name = ticker + '_volume'
                    tablename = 'exchange_stockprice_' + name
                    val_arr.append("('%s', '%s', '%s', '%s', '%s', '%s')" % ('exchange', 'stockprice', 'us', name, tablename, 'timeseries'))

                    if index > 500:
                        index = 0
                        val_str = ','.join(val_arr)
                        query_str = 'INSERT INTO data_source (type, subtype, country, name, tablename, tabletype) VALUES ' + val_str
                        cursor2.execute(query_str)
                        connection.commit()
                        val_arr = []
                except Exception as e:
                    print e
        except Exception as e:
            print e

def populate_data_source_with_metrics_info():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES LIKE '%_metrics'")
            data = cursor.fetchall()
            for row in data:
                try:
                    tablename = row[0].lower()
                    name = tablename.replace('company_fundamentals_', '')
                    query_str = "INSERT INTO data_source (type, subtype, country, name, tablename, tabletype) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % ('company', 'fundamentals', 'us', name, tablename, 'transactions')
                    cursor2 = connection.cursor()
                    cursor2.execute(query_str)
                    connection.commit()
                except Exception as e:
                    print e
        except Exception as e:
            print e

def populate_data_source_with_rogue_ticker_tables():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            data = validate_database.find_rogue_table()
            for row in data:
                try:
                    tablename = row.lower()
                    name = tablename.replace('exchange_stockprice_', '')
                    query_str = "INSERT INTO data_source (type, subtype, country, name, tablename, tabletype) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % ('exchange', 'stockprice', 'us', name, tablename, 'timeseries')
                    print query_str
                    cursor2 = connection.cursor()
                    cursor2.execute(query_str)
                    connection.commit()
                except Exception as e:
                    print e
        except Exception as e:
            print e

populate_data_source_with_rogue_ticker_tables()
#populate_data_source_with_ticker_info()
#populate_data_source_with_metrics_info()


