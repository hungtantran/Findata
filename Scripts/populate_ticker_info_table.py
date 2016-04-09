__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from dao_factory_repo import DAOFactoryRepository
from sec_ticker_info_helper import SecTickerInfoHelper


# Assume the file has there columns:
# "Symbol","Name","LastSale","MarketCap","ADR TSO","IPOyear","Sector","Industry","Summary Quote"
def populate_ticker_info_table(company_info_file, exchange=None):
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()


            with open(company_info_file) as f:
                lines = f.read().split('\n')
                for i in range(1, len(lines)):
                    line = lines[i]
                    cells = line.split('",')
                    cells = [cell.replace('"', '') for cell in cells]

                    ticker = cells[0]
                    name = cells[1]

                    try:
                        ipo_year = int(cells[5])
                    except Exception as e:
                        ipo_year = None

                    sector = cells[6]
                    if sector == 'n/a':
                        sector = None

                    industry = cells[7]
                    if industry == 'n/a':
                        industry = None

                    print '%s, %s, %s, %s, %s' % (ticker, name, ipo_year, sector, industry)
                    cursor.execute("INSERT INTO ticker_info (ticker, name, ipo_year, sector, industry, exchange) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE "
                                   "KEY UPDATE name=%s, ipo_year=%s, sector=%s, industry=%s, exchange=%s", (ticker, name, ipo_year, sector, industry, exchange, name,
                                   ipo_year, sector, industry, exchange))
                    connection.commit()

        except Exception as e:
            print e


def populate_cik():
    sec_ticker_info_helper = SecTickerInfoHelper(dbtype=None, username=None, password=None, server=None, database=None)
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute('SELECT name from ticker_info where cik is null')
            data = cursor.fetchall()
            for row in data:
                name = row[0]
                cik = sec_ticker_info_helper.company_name_to_cik(company_name=name)
                print 'Update company %s with cik %s' % (name, cik)
                cursor2 = connection.cursor()
                cursor2.execute('UPDATE ticker_info SET cik=%s WHERE name=%s', (cik, name))

        except Exception as e:
            print e

populate_cik()
#populate_ticker_info_table(company_info_file='Data/amex_company_list.csv', exchange='NYSEMKT')
#populate_ticker_info_table(company_info_file='Data/nyse_company_list.csv', exchange='NYSE')
#populate_ticker_info_table(company_info_file='Data/nasdaq_company_list.csv', exchange='NASDAQ')
