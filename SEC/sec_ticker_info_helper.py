__author__ = 'hungtantran'


import datetime
import os
import re
import zipfile
from lxml import etree

import logger
from string_helper import StringHelper
from dao_factory_repo import DAOFactoryRepository


class SecTickerInfoHelper(object):
    def __init__(self, dbtype, username, password, server, database):
        self.cik_to_ticker_map = {}
        self.ticker_to_cik_map = {}

        dao_factory = DAOFactoryRepository.getInstance(dbtype)
        with dao_factory.create(username, password, server, database) as connection:
            try:
                # TODO need to make this general
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM ticker_info")
                data = cursor.fetchall()
                for row in data:
                    if (row[0] is None) or (row[1] is None):
                        continue
                    self.cik_to_ticker_map[int(row[0])] = row[1]
                    self.ticker_to_cik_map[row[1]] = int(row[0])
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def cik_to_ticker(self, cik):
        if cik in self.cik_to_ticker_map:
            return self.cik_to_ticker_map[cik]
        return None

    def ticker_to_cik(self, ticker):
        if ticker in self.ticker_to_cik_map:
            return self.ticker_to_cik_map[ticker]
        return None
