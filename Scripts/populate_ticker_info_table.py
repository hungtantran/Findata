__author__ = 'hungtantran'


import filecmp
import os
from os import listdir, rename
from os.path import isfile, join
import re
import unittest
import zipfile

import logger
from constants_config import Config
from dao_factory_repo import DAOFactoryRepository
from sec_ticker_info_helper import SecTickerInfoHelper
from sec_xbrl_helper import SecXbrlHelper
from string_helper import StringHelper
from sec_xbrl_processor import SecXbrlProcessor


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


def populate_cik_from_xbrl_zip_directory(xbrl_zip_directory):
    cik_to_ticker_map, ticker_to_cik_map = build_cik_ticker_map_from_xbrl_zip_directory(xbrl_zip_directory)

    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute('SELECT ticker, cik from ticker_info')
            data = cursor.fetchall()

            cursor2 = connection.cursor()
            for row in data:
                try:
                    ticker = row[0]
                    cik = row[1]

                    if ticker not in ticker_to_cik_map:
                        continue

                    found_cik = ticker_to_cik_map[ticker]
                    if (cik is not None) and (found_cik == cik):
                        continue

                    if (found_cik != cik) and (cik is not None):
                        print "%s %s %s" % (ticker, found_cik, cik)

                    cik_int = int(found_cik)
                    update_query = "UPDATE ticker_info SET cik=%d WHERE ticker='%s'" % (cik_int, ticker)
                    print update_query

                    cursor2.execute(update_query)
                    connection.commit()
                except Exception as e:
                    print e

        except Exception as e:
            print e


def build_cik_ticker_map_from_xbrl_zip_directory(xbrl_zip_directory):
    xbrl_zip_files = [f for f in listdir(xbrl_zip_directory) if (isfile(join(xbrl_zip_directory, f)) and f.endswith('.zip'))]

    ticker_to_cik_info_map = {}
    for zip_file in xbrl_zip_files:
        (ticker, cik, year, quarter, form_name) = SecXbrlProcessor.parse_xbrl_zip_file_name(zip_file)

        if (ticker is None or cik is None or year is None or quarter is None or form_name is None):
            #print zip_file
            continue

        if ticker in ticker_to_cik_info_map:
            info = ticker_to_cik_info_map[ticker]
            if (info[0] != cik) and ((info[1] < year) or (
                info[1] == year and info[2] < quarter)):
                print 'Update cik for %s from %d to %d' % (ticker, info[0], cik)
                ticker_to_cik_info_map[ticker] = [cik, year, quarter]
        else:
            ticker_to_cik_info_map[ticker] = [cik, year, quarter]

    ticker_to_cik_map = {}
    for ticker in ticker_to_cik_info_map:
        ticker_to_cik_map[ticker.upper()] = ticker_to_cik_info_map[ticker][0]

    cik_to_ticker_map = {}
    for ticker in ticker_to_cik_map:
        cik_to_ticker_map[ticker_to_cik_map[ticker]] = ticker

    return cik_to_ticker_map, ticker_to_cik_map


if __name__ == '__main__':
    #populate_cik_from_xbrl_zip_directory('SEC/xbrl_zip_files')
    #build_cik_ticker_map_from_xbrl_zip_directory('SEC/xbrl_zip_files')
    #populate_ticker_info_table(company_info_file='Data/amex_company_list.csv', exchange='NYSEMKT')
    #populate_ticker_info_table(company_info_file='Data/nyse_company_list.csv', exchange='NYSE')
    #populate_ticker_info_table(company_info_file='Data/nasdaq_company_list.csv', exchange='NASDAQ')
