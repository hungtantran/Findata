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
    SUMMARY_LINKS_TEMPLATE = 'http://finance.yahoo.com/q/hp?s=%s&z=66&y=%d'
    SUMMARY_DIMENSIONS = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
    NUM_RETRIES_DOWNLOAD = 2
    WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC = 1
    MAX_PROCESSING_THREADS = 5
    UPDATE_FREQUENCY_SECONDS = 43200


    def __init__(self, db_type, username, password, server, database, max_num_threads=None, update_frequency_seconds=None, update_history=False):
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
                logger.Logger.log(logger.LogLevel.INFO, 'Wait for thread %s' % wait_thread.name)
                wait_thread.join()
                logger.Logger.log(logger.LogLevel.INFO, 'Thread %s done' % wait_thread.name)

            logger.Logger.log(logger.LogLevel.INFO,
                    'Sleep for %d secs before updating again' % self.update_frequency_seconds)
            # TODO make it sleep through weekend
            time.sleep(self.update_frequency_seconds)

    def populate_work_queue(self):
        raise NotImplementedError('Need to implement populate_work_queue')

    def get_metric_table_name(self, metric):
        return '%s_metrics' % metric.ticker

    def get_list_of_crawl_pages(self, latest_time, earliest_time):
        crawl_pages = []
        today = datetime.datetime.today()

        latest_diff = None
        if latest_time is not None:
            latest_diff = today - latest_time
            # 66 trading days per page = (approx) 90 normal days
            crawl_pages.extend(range(int(latest_diff.days/90) + 1))

        earliest_diff = None
        if earliest_time is not None:
            earliest_diff = today - earliest_time
            crawl_pages.extend(range(int(earliest_diff.days/90), 1000))

        if len(crawl_pages) == 0:
            crawl_pages = range(1000)

        crawl_pages = list(set(crawl_pages))
        crawl_pages.sort()
        # Marked days are days that we might already crawl but we recrawl to make sure we don't
        # miss any data
        marked_days = []

        if latest_diff is not None and earliest_diff is not None:
            [int(latest_diff.days/90), int(earliest_diff.days/90)]
        return crawl_pages, marked_days

    def update_metrics(self):
        count = 0
        while not self.q.empty():
            try:
                count += 1
                metric = self.q.get()

                logger.Logger.log(logger.LogLevel.INFO, '(%s) Processing metric %s (%s) and push to database' % (
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

                latest_time, earliest_time = metrics_db.get_earliest_and_latest_time()
                logger.Logger.log(logger.LogLevel.INFO, 'Found for metric %s (%s) latest time: %s, earliest time: %s' % (metric.name, metric.ticker, latest_time, earliest_time))

                # Normal case: only update first page. Special case: update all pages later than latest and earlier than earliest
                crawl_pages = [0]
                marked_days = []
                if self.update_history:
                    crawl_pages, marked_days = self.get_list_of_crawl_pages(latest_time, earliest_time)
                # If the lastest time is Friday of this week and today is Saturday or Sunday, skip the entry since we already have the latest value
                else:
                    today = datetime.datetime.today()
                    delta_day = today - latest_time
                    if (latest_time.weekday() == 4 and today.weekday() >= 4 and delta_day.days < 7):
                        logger.Logger.log(logger.LogLevel.INFO, 'Already have the latest data for %s at date %s, skip' % (metric.ticker, latest_time))
                        continue

                for page_num in crawl_pages:
                    data = self.update_metric_value(metric, page_num)
                    if len(data) == 0:
                        logger.Logger.log(logger.LogLevel.INFO, 'Found no more data for metric %s (%s) at page %d' % (metric.name, metric.ticker, page_num))
                        break

                    logger.Logger.log(logger.LogLevel.INFO, 'Update database for %s with given data' % metric.name)
                    num_update= metrics_db.update_database_with_given_data(
                            data=data,
                            latest_time=latest_time,
                            earliest_time=earliest_time)
                    if num_update == 0 and page_num not in marked_days:
                        logger.Logger.log(logger.LogLevel.INFO, 'Update to the latest data for metric %s (%s) at page %d' % (metric.name, metric.ticker, page_num))
                        break

                logger.Logger.log(logger.LogLevel.INFO, 'Sleep for %d secs before updating again' %
                        UpdateYahooFinance.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)
                time.sleep(UpdateYahooFinance.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)
            finally:
                self.q.task_done()

    def update_metric_value(self, metric, page_num):
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Update metric %s (%s) now for page %d' % (metric.name, metric.ticker, page_num))
            response = urllib.urlopen(UpdateYahooFinance.SUMMARY_LINKS_TEMPLATE % (metric.ticker, 66 * page_num))
            html_string = response.read()
            data = self.update_from_html_content(html_string)
            return data
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def _yahoo_finance_get_content_table(self, html_elem):
        outer_content_table_elem = html_elem.findAll('table', attrs={'class': 'yfnc_datamodoutline1'})
        if len(outer_content_table_elem) != 1:
            logger.Logger.log(logger.LogLevel.ERROR, 'Found %d outer content table' % len(outer_content_table_elem))
            return None

        inner_content_table_elem = outer_content_table_elem[0].findAll('table')
        if len(inner_content_table_elem) != 1:
            logger.Logger.log(logger.LogLevel.ERROR, 'Found %d inner content table' % len(inner_content_table_elem))
            return None

        return inner_content_table_elem[0]

    def _yahoo_finance_extract_titles(self, header_elem):
        titles_elem = header_elem.findAll('th')
        if len(titles_elem) == 0:
            return None

        if titles_elem[0].get_text() != 'Date':
            return None

        titles = []
        for i in range(1, len(titles_elem)):
            titles.append(StringHelper.clean_name(titles_elem[i].get_text()))

        logger.Logger.log(logger.LogLevel.INFO, 'Found titles %s' % titles)
        return titles

    def update_from_html_content(self, html_string):
        num_fail = 0
        data = []
        try:
            html_elem = BeautifulSoup(html_string, 'html.parser')

            # Get the table html elem
            content_table_elem = self._yahoo_finance_get_content_table(html_elem)
            if content_table_elem is None:
                logger.Logger.log(logger.LogLevel.WARN, 'Exit found no content table')
                return

            rows_elem = content_table_elem.findAll('tr')
            if len(rows_elem) == 0:
                logger.Logger.log(logger.LogLevel.INFO, 'Exit found no row values left')
                return

            # Extract the title
            header_elem = rows_elem[0]
            titles = self._yahoo_finance_extract_titles(header_elem)
            if (titles is None) or (len(titles) != len(UpdateYahooFinance.SUMMARY_DIMENSIONS)):
                logger.Logger.log(logger.LogLevel.INFO, 'Does not find the expected titles')
                return

            # Iterate through each row in the table, extract date and value
            for i in range(1, len(rows_elem)):
                row_elem = rows_elem[i]
                tds_elem = row_elem.findAll('td')

                # The +1 is to account for the Date column, not in titles array
                # For special rows of dividends and stock split, there are 2 td elems
                if (len(tds_elem) != len(titles) + 1 and len(tds_elem) != 2):
                    logger.Logger.log(logger.LogLevel.WARN, 'Row with num elem %d not match with num titles %d' %
                                      (len(tds_elem), len(titles)))
                    continue

                date = StringHelper.convert_string_to_datetime(tds_elem[0].get_text())
                if date is None:
                    logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to date' % tds_elem[0].get_text())
                    continue

                # For normal stock price rows:
                if (len(tds_elem) == len(titles) + 1):
                    for j in range(1, len(tds_elem)):
                        cell_text = tds_elem[j].get_text().strip()
                        cell_value = StringHelper.parse_value_string(cell_text)
                        if cell_value is None:
                            logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to value' % cell_text)
                            continue

                        value = metrics.Metrics(
                                metric_name=UpdateYahooFinance.SUMMARY_DIMENSIONS[j - 1],
                                start_date=date,
                                end_date=date,
                                unit='usd',
                                value=cell_value)
                        data.append(value)
                elif len(tds_elem) == 2:
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
            return data