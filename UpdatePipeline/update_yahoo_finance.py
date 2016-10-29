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
import metrics
import metrics_database
from ticker_info_database import TickerInfoDatabase
from string_helper import StringHelper
from Common.constants_config import Config


class UpdateYahooFinance(threading.Thread):
    SUMMARY_LINKS_TEMPLATE = 'http://chart.finance.yahoo.com/table.csv?s=%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=d&ignore=.csv'
    SUMMARY_DIMENSIONS = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
    CSV_HEADERS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
    NUM_RETRIES_DOWNLOAD = 2
    WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC = 3
    MAX_PROCESSING_THREADS = 5
    UPDATE_FREQUENCY_SECONDS = 43200
    MAX_PAGE_SIZE = 90


    def __init__(self, db_type, username, password, server, database,
                 max_num_threads=None, update_frequency_seconds=None,
                 update_history=False):
        threading.Thread.__init__(self)

        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database

        self.update_frequency_seconds = update_frequency_seconds or UpdateYahooFinance.UPDATE_FREQUENCY_SECONDS
        self.max_num_threads = max_num_threads or UpdateYahooFinance.MAX_PROCESSING_THREADS
        self.update_history = update_history
        self.q = Queue.Queue()

        self.ticker_info_db = TickerInfoDatabase(
            self.db_type,
            self.username,
            self.password,
            self.server,
            self.database)

    def sanitize_metric(self, metric):
        metric.ticker = metric.ticker.lower()

    def run(self):
        while True:
            self.populate_work_queue()

            # Start threads to update
            threads = []
            for i in range(self.max_num_threads):
                t = threading.Thread(target=self.update_metrics)
                threads.append(t)
                t.start()

            for i in range(len(threads)):
                wait_thread = threads[i]
                logger.Logger.info('Wait for thread %s' % wait_thread.name)
                wait_thread.join()
                logger.Logger.info('Thread %s done' % wait_thread.name)

            logger.Logger.info(
                    'Sleep for %d secs before updating again' % self.update_frequency_seconds)
            # TODO make it sleep through weekend
            time.sleep(self.update_frequency_seconds)

    def populate_work_queue(self):
        raise NotImplementedError('Need to implement populate_work_queue')

    def get_metric_table_name(self, metric):
        return 'ticker_info_%s_metrics' % metric.id

    def get_csv_link(self, metric, beginning_date, end_date):
        return UpdateYahooFinance.SUMMARY_LINKS_TEMPLATE % (
                metric.ticker,
                beginning_date.month - 1,
                beginning_date.day,
                beginning_date.year,
                end_date.month - 1,
                end_date.day,
                end_date.year)

    def get_unit(self):
        return 'usd'

    def get_metric_name(self, metric, dimension):
        return dimension

    def get_earliest_and_latest_time(self, metric, metrics_db):
        return metrics_db.get_earliest_and_latest_time(metric_name='adj_close')

    def get_list_of_crawl_pages(self, latest_time, earliest_time):
        crawl_pages = []
        today = datetime.datetime.today()

        latest_diff = None
        if latest_time is not None:
            latest_diff = today - latest_time
            crawl_pages.extend(range(int(latest_diff.days/UpdateYahooFinance.MAX_PAGE_SIZE) + 1))

        earliest_diff = None
        if earliest_time is not None:
            earliest_diff = today - earliest_time
            crawl_pages.extend(range(int(earliest_diff.days/UpdateYahooFinance.MAX_PAGE_SIZE), 1000))

        if len(crawl_pages) == 0:
            crawl_pages = range(1000)

        crawl_pages = list(set(crawl_pages))
        crawl_pages.sort()
        # Marked days are days that we might already crawl but we recrawl to make sure we don't
        # miss any data
        marked_days = []

        if latest_diff is not None and earliest_diff is not None:
            [int(latest_diff.days/UpdateYahooFinance.MAX_PAGE_SIZE), int(earliest_diff.days/UpdateYahooFinance.MAX_PAGE_SIZE)]
        return crawl_pages, marked_days

    def update_metrics(self):
        count = 0
        while not self.q.empty():
            try:
                count += 1
                metric = self.q.get()

                logger.Logger.info(
                        '(%s) Processing metric %s (%s) and push to database' % (
                        threading.current_thread().name, metric.name, metric.ticker))

                self.sanitize_metric(metric)
                # TODO make this more extensible
                if not metric.ticker.isalnum():
                    continue

                tablename = self.get_metric_table_name(metric)
                metrics_db = metrics_database.MetricsDatabase(
                        self.db_type,
                        self.username,
                        self.password,
                        self.server,
                        self.database,
                        tablename)
                metrics_db.create_metric()

                latest_time, earliest_time = self.get_earliest_and_latest_time(
                        metric, metrics_db)
                logger.Logger.info(
                        'Found for metric %s (%s) latest time: %s, earliest time: %s' % (
                        metric.name, metric.ticker, latest_time, earliest_time))

                # Normal case: only update first page. Special case: update all
                # pages later than latest and earlier than earliest
                crawl_pages = [0]
                marked_days = []
                if self.update_history:
                    crawl_pages, marked_days = self.get_list_of_crawl_pages(latest_time, earliest_time)
                # If the lastest time is Friday of this week and today is
                # Saturday or Sunday, skip the entry since we already have the
                # latest value
                elif latest_time is not None:
                    today = datetime.datetime.today()
                    delta_day = today - latest_time
                    if (latest_time.weekday() == 4 and today.weekday() >= 4 and delta_day.days < 7):
                        logger.Logger.info(
                                'Already have the latest data for %s at date %s, skip' % (
                                metric.ticker, latest_time))
                        continue

                for page_num in crawl_pages:
                    data = self.update_metric_value(metric, page_num)
                    if len(data) == 0:
                        logger.Logger.info(
                                'Found no more data for metric %s (%s) at page %d' % (
                                metric.name, metric.ticker, page_num))
                        break
                    logger.Logger.info('Update database for %s with given data' % metric.name)
                    num_update= metrics_db.update_database_with_given_data(
                            data=data,
                            latest_time=latest_time,
                            earliest_time=earliest_time)
                    if num_update == 0 and page_num not in marked_days:
                        logger.Logger.info(
                                'Update to the latest data for metric %s (%s) at page %d' % (
                                metric.name, metric.ticker, page_num))
                        break

                logger.Logger.info('Sleep for %d secs before updating again' %
                        UpdateYahooFinance.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)
                time.sleep(UpdateYahooFinance.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)
            finally:
                self.q.task_done()

    def update_metric_value(self, metric, page_num):
        try:
            today = datetime.datetime.today()
            end_date = today - datetime.timedelta(days=page_num*UpdateYahooFinance.MAX_PAGE_SIZE)
            beginning_date = end_date - datetime.timedelta(days=UpdateYahooFinance.MAX_PAGE_SIZE)
            csv_link = self.get_csv_link(metric, beginning_date, end_date)
            logger.Logger.log(logger.LogLevel.INFO,
                              'Update metric %s (%s) now for page %d from %s to %s' % (
                              metric.name, metric.ticker, page_num,
                              beginning_date, end_date)) 

            response = urllib.urlopen(csv_link)
            csv_string = response.read()
            data = self.update_from_csv_content(metric, csv_string)
            return data
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def update_from_csv_content(self, metric, csv_string):
        num_fail = 0
        data = []
        try:
            lines = csv_string.split('\n')
            if len(lines) == 0:
                logger.Logger.warn('Exit found no content')
                return data

            headers = lines[0].split(',')
            if len(headers) != len(UpdateYahooFinance.CSV_HEADERS):
                logger.Logger.warn('Found unexpected headers %s' % headers)
                return data

            for i, header in enumerate(headers):
                if header != UpdateYahooFinance.CSV_HEADERS[i]:
                    logger.Logger.warn('Found unexpected headers %s' % headers)
                    return data

            for i in range(1, len(lines)):
                cells = lines[i].split(',')
                if len(cells) != len(UpdateYahooFinance.CSV_HEADERS):
                    logger.Logger.warn('Found unexpected line %s' % lines[i])
                    continue

                date = StringHelper.convert_string_to_datetime(cells[0])
                for j in range(1, len(cells)):
                    cell_value = StringHelper.parse_value_string(cells[j])
                    value = metrics.Metrics(
                            metric_name=self.get_metric_name(
                                    metric,
                                    UpdateYahooFinance.SUMMARY_DIMENSIONS[j - 1]),
                            start_date=date,
                            end_date=date,
                            unit=self.get_unit(),
                            value=cell_value)
                    data.append(value)
        except Exception as e:
            logger.Logger.error(e)
        finally:
            return data

    def update_dividend(self):
        """elif len(tds_elem) == 2:
            # For special dividends and stock splits rows
            cell_text = tds_elem[1].get_text().strip()
            if 'Dividend' in cell_text:
                # Cell text is like this '0.48 Dividend'
                dividend_value_string = cell_text.replace(' Dividend', '').strip()
                dividend_value = StringHelper.parse_value_string(dividend_value_string)
                value = metrics.Metrics(
                        metric_name='dividend',
                        start_date=date,
                        end_date=date,
                        unit='usd',
                        value=dividend_value)
                data.append(value)
            elif cell_text.endswith('Stock Split'):
                # Cell text is like this '1: 5 Stock Split'
                cell_value_string = cell_text.replace(' Stock Split', '').strip().split(':')
                cell_value = StringHelper.parse_value_string(cell_value_string[0]) / StringHelper.parse_value_string(cell_value_string[1])
                value = metrics.Metrics(
                        metric_name='stock split',
                        start_date=date,
                        end_date=date,
                        unit='ratio',
                        value=cell_value)
                data.append(value)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            return data"""
        pass