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
import metrics
import ticker_info
import ticker_info_database
import metrics_database
from string_helper import StringHelper
from Common.constants_config import Config
from update_yahoo_finance import UpdateYahooFinance


class UpdateExchangeIndex(UpdateYahooFinance):
    MAX_PROCESSING_THREADS = 1

    SUMMARY_LINKS_TEMPLATE = {
        'dowjones': 'http://chart.finance.yahoo.com/table.csv?s=^DJI&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv',
        'sp500': 'http://chart.finance.yahoo.com/table.csv?s=^GSPC&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv',
        'nasdaq': 'http://chart.finance.yahoo.com/table.csv?s=^IXIC&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv',
    }

    def __init__(self, db_type, username, password, server, database,
                 max_num_threads=None, update_frequency_seconds=None,
                 update_history=False):
        super(UpdateExchangeIndex, self).__init__(
                db_type=db_type,
                username=username,
                password=password,
                server=server,
                database=database,
                max_num_threads=max_num_threads,
                update_frequency_seconds=update_frequency_seconds,
                update_history=update_history)

        self.ticker_info_db = ticker_info_database.TickerInfoDatabase(
                self.db_type,
                self.username,
                self.password,
                self.server,
                self.database)

    def populate_work_queue(self):
        sp500_ticker_info = ticker_info.TickerInfo(ticker='sp500', name='sp500')
        dowjones_ticker_info = ticker_info.TickerInfo(ticker='dowjones', name='dowjones')
        nasdaq_ticker_info = ticker_info.TickerInfo(ticker='nasdaq', name='nasdaq')
        
        self.q.put(sp500_ticker_info)
        self.q.put(dowjones_ticker_info)
        self.q.put(nasdaq_ticker_info)

    def get_metric_table_name(self, metric):
        return 'exchange_index_metrics'

    def get_csv_link(self, metric, beginning_date, end_date):
        return UpdateExchangeIndex.SUMMARY_LINKS_TEMPLATE[metric.ticker] % (
                beginning_date.month - 1,
                beginning_date.day,
                beginning_date.year,
                end_date.month - 1,
                end_date.day,
                end_date.year)

    def get_unit(self):
        return 'point'

    def get_metric_name(self, metric, dimension):
        return '%s_%s' % (metric.ticker, dimension)

    def get_earliest_and_latest_time(self, metric, metrics_db):
        return metrics_db.get_earliest_and_latest_time('%s_adj_close' % metric.ticker)


def main():
    try:
        update_obj = UpdateExchangeIndex(
                'mysql',
                Config.mysql_username,
                Config.mysql_password,
                Config.mysql_server,
                Config.mysql_database,
                update_history=False,
                max_num_threads=UpdateExchangeIndex.MAX_PROCESSING_THREADS)
        update_obj.daemon = True
        update_obj.start()

        while True:
            time.sleep(1)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
