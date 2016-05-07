__author__ = 'hungtantran'

import datetime
import re
import urllib
import time
import threading
from bs4 import BeautifulSoup
import string
import Queue

import logger
import metrics_database
import ticker_info_database
from string_helper import StringHelper
from Common.constants_config import Config
from update_yahoo_finance import UpdateYahooFinance


class UpdateExchangeFund(UpdateYahooFinance):
    FUND_LIST_LINK_TEMPLATE = 'http://www.marketwatch.com/tools/mutual-fund/list/%s'

    def __init__(self, db_type, username, password, server, database, max_num_threads=None, update_frequency_seconds=None, update_history=False, update_list=False):
        super(UpdateExchangeFund, self).__init__(
                db_type=db_type,
                username=username,
                password=password,
                server=server,
                database=database,
                max_num_threads=max_num_threads,
                update_frequency_seconds=update_frequency_seconds,
                update_history=update_history)
        self.update_list = update_list

    def populate_work_queue(self):
        if self.update_list:
            fund_list = self.get_latest_fund_list()
            self.update_fund_list(fund_list)
        else:
            fund_list = self.ticker_info_db.get_ticker_info_data(ticker_type='fund')

        for fund in fund_list:
            self.q.put(fund)

    def get_latest_fund_list(self):
        fund_list = []
        for letter in string.ascii_uppercase:
            cur_link = UpdateExchangeFund.FUND_LIST_LINK_TEMPLATE % letter
            logger.Logger.log(logger.LogLevel.INFO, 'Get latest fund list from link %s' % cur_link)

            response = urllib.urlopen(cur_link)
            html_string = response.read()
            new_fund_list = self.parse_fund_list_from_html(html_string)
            logger.Logger.log(logger.LogLevel.INFO, 'Found %d funds' % len(new_fund_list))
            fund_list.extend(new_fund_list)
        return fund_list

    def parse_fund_list_from_html(self, html_string):
        fund_list = []

        try:
            html_elem = BeautifulSoup(html_string, 'html.parser')
            table_elems = html_elem.findAll('table')
            if len(table_elems) != 1:
                logger.Logger.log(logger.LogLevel.ERROR, 'Found %d content table' % len(table_elems))
                return fund_list

            row_elems = table_elems[0].findAll('tr')
            for i in range(1, len(row_elems)):
                row_elem = row_elems[i]
                symbol_elems = row_elem.findAll('td', attrs={'class': 'quotelist-symb'})
                name_elems = row_elem.findAll('td', attrs={'class': 'quotelist-name'})
                if len(symbol_elems) != 1 or len(name_elems) != 1:
                    logger.Logger.log(logger.LogLevel.ERROR, 'Found %d symbol, %d name' % (len(symbol_elems), len(name_elems)))
                    continue

                # Symbol text should be like 'ACSBX;
                # Name text should be like 'Avenue Mutual Fund Trust: Avenue Credit Strategies Fund; Institutional Class Shares'
                ticker = symbol_elems[0].get_text().strip()
                name = None
                family = None
                class_share = None

                full_name = name_elems[0].get_text()
                parts = full_name.split(';')

                if len(parts) >= 2:
                    class_share = parts[1].strip()

                name_and_family = parts[0].split(':')
                family = name_and_family[0].strip()
                if len(name_and_family) >= 2:
                    name = name_and_family[1].strip()

                fund = fund_info.FundInfo(
                        id=None,
                        ticker=ticker,
                        name=name,
                        family=family,
                        class_share=class_share,
                        fund_type=None,
                        metadata=None)
                fund_list.append(fund)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

        return fund_list


def main():
    try:
        update_obj = UpdateExchangeFund(
                'mysql',
                Config.mysql_username,
                Config.mysql_password,
                Config.mysql_server,
                Config.mysql_database,
                update_history=True)
        update_obj.daemon = True
        update_obj.start()

        while True:
            time.sleep(1)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
