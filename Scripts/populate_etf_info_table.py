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
def populate_etf_info_table(company_info_file, exchange=None):
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

                    print '%s, %s, %s, %s, %s' % (ticker, name, ipo_year, sector, industry)
                    cursor.execute("INSERT INTO etf_info (ticker, name, asset_class, sector, location, metadata) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE "
                                   "KEY UPDATE name=%s, asset_class=%s, sector=%s, location=%s, metadata=%s", (ticker, name, None, None, None, None, name, None, None, None, None))
                    connection.commit()

        except Exception as e:
            print e


if __name__ == '__main__':
    populate_etf_info_table('Data/etf_list.csv')