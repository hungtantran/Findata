__author__ = 'hungtantran'

import init_app
import datetime
import re
import urllib
import time
import threading
from bs4 import BeautifulSoup
import string
import Queue

import logger
import ticker_info_database
import metrics
import metrics_database
from string_helper import StringHelper
from Common.constants_config import Config
from update_yahoo_finance import UpdateYahooFinance


class UpdateExchangeETF(UpdateYahooFinance):
    MAX_PROCESSING_THREADS = 2

    def __init__(self, db_type, username, password, server, database,
                 max_num_threads=None, update_frequency_seconds=None,
                 update_history=False):
        super(UpdateExchangeETF, self).__init__(
                db_type=db_type,
                username=username,
                password=password,
                server=server,
                database=database,
                max_num_threads=max_num_threads,
                update_frequency_seconds=update_frequency_seconds,
                update_history=update_history)

    def populate_work_queue(self):
        etf_list = self.ticker_info_db.get_ticker_info_data(ticker_type='etf')

        for etf in etf_list:
            self.q.put(etf)


def main():
    try:
        update_obj = UpdateExchangeETF(
                'mysql',
                Config.mysql_username,
                Config.mysql_password,
                Config.mysql_server,
                Config.mysql_database,
                update_history=False,
                max_num_threads=UpdateExchangeETF.MAX_PROCESSING_THREADS)
        update_obj.daemon = True
        update_obj.start()

        while True:
            time.sleep(1)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
