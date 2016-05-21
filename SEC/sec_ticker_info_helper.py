__author__ = 'hungtantran'


import datetime
import os
import re
import zipfile
from lxml import etree
import urllib, urllib2
from bs4 import BeautifulSoup
import time

import logger
from string_helper import StringHelper
from ticker_info_database import TickerInfoDatabase


class SecTickerInfoHelper(object):
    def __init__(self, dbtype, username, password, server, database):
        self.cik_to_ticker_map = {}
        self.ticker_to_cik_map = {}

        try:
            ticker_info_db = TickerInfoDatabase(
                    dbtype,
                    username,
                    password,
                    server,
                    database,
                    'ticker_info')

            data = ticker_info_db.get_ticker_info_data()
            for row in data:
                if (row.cik is None) or (row.ticker is None):
                    continue
                self.cik_to_ticker_map[row.cik] = row.ticker
                self.ticker_to_cik_map[row.ticker] = row.cik
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

    @staticmethod
    def company_name_to_cik(company_name):
        try:
            sec_url = 'http://www.sec.gov/cgi-bin/cik_lookup'
            values = dict(company=company_name)
            data = urllib.urlencode(values)
            req = urllib2.Request(sec_url, data)
            rsp = urllib2.urlopen(req)
            response = rsp.read()

            html_elem = BeautifulSoup(response, 'html.parser')
            pre_elems = html_elem.find_all('pre')
            if len(pre_elems) != 2:
                return None

            cik = None
            link_elems = pre_elems[1].find_all('a')
            for link_elem in link_elems:
                cur_cik = StringHelper.parse_value_string(link_elem.get_text())
                # There are more than 2 ciks returned, can't decide
                if cik != None and cik != cur_cik:
                    return None
                cik = cur_cik

            return int(cik)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

