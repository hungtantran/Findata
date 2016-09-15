#
#

__author__ = 'hungtantran'

import init_app

import datetime
import re
import urllib
import time
import threading
import json
import urllib, urllib2
from bs4 import BeautifulSoup
import string
import Queue
import HTMLParser
import unicodedata

import logger
import metrics
import metrics_database
import ticker_info_database
from economics_info_database import EconomicsInfoDatabase
from economics_info import EconomicsInfo
from string_helper import StringHelper
from Common.constants_config import Config


class UpdateBureauEconomicAnalysis(threading.Thread):
    DATA_PAGE = {
        'GDP & Personal Income': 'http://www.bea.gov//national/nipaweb/DownSS2.asp',
        'Fixed Assets': 'http://www.bea.gov//national/FA2004/DownSS2.asp'
    }
    NUM_RETRIES_DOWNLOAD = 2
    WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC = 20
    MAX_PROCESSING_THREADS = 5
    UPDATE_FREQUENCY_SECONDS = 86400

    def __init__(
            self, db_type, username, password, server, database,
            max_num_threads=None, update_frequency_seconds=None,
            update_history=False):
        threading.Thread.__init__(self)

        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.update_history = update_history
        self.q = Queue.Queue()

        self.update_frequency_seconds = (
                update_frequency_seconds or
                UpdateBureauEconomicAnalysis.UPDATE_FREQUENCY_SECONDS)

        self.max_num_threads = (
                max_num_threads or
                UpdateBureauEconomicAnalysis.MAX_PROCESSING_THREADS)

        self.economics_info_db = EconomicsInfoDatabase(
                self.db_type,
                self.username,
                self.password,
                self.server,
                self.database)

    def run(self):
        while True:
            self.update_measures()
            # TODO make it sleep through weekend
            logger.Logger.info('Sleep for %d secs before updating again' % (
                    self.update_frequency_seconds))
            time.sleep(self.update_frequency_seconds)
    
    # TODO move this function to general utilities
    def download_link_content(self, link):
        response = urllib.urlopen(link)
        return response.read()

    def get_csv_links(self, link):
        page_content = self.download_link_content(link)
        matches = re.findall('"([^"]*\.csv[^"]*)"', page_content)
        root_link = link[:link.rfind('/')]
        csv_links = [root_link + '/' + match for match in matches]
        logger.Logger.info('Found csv links %s' % (csv_links))
        return csv_links

    def get_csv_content(self, csv_link):
        logger.Logger.info('Get csv content for %s' % csv_link)
        csv_content = self.download_link_content(csv_link)
        logger.Logger.info('Download csv content with length %d' % len(csv_content))
        return csv_content

    def trim_ending_comma(self, str):
        for i in reversed(range(len(str))):
            if str[i] != ',':
                str = str[:i+1]
                break
            elif str[i] == ',' and i == 0:
                str = ''
        return str

    def split_line_into_values(self, str):
        in_double_quote = False
        chars = list(str)
        values = []
        curVal = ''
        for i in range(len(chars)):
            if chars[i] == '"':
                in_double_quote = False if in_double_quote else True
            elif chars[i] == ',' and not in_double_quote:
                values.append(curVal)
                curVal = ''
            else:
                curVal += chars[i]
        values.append(curVal)
        return values

    def num_starting_whitespace(self, str):
        num_starting_whitespace = 0
        for i in range(len(str)):
            if str[i] == ' ':
                num_starting_whitespace += 1
            else:
                break
        return num_starting_whitespace

    def update_data_from_csv_content(self, csv_content):
        lines = csv_content.split('\n')
        type = None
        unit = None
        headers = None
        quarters = None
        category_stack = []

        # Data is a array. Each element is an array itself [type, full_name, name_code, unit, data_values]
        #   [type, full_name, name_code, unit] like [' Current-Cost Net.....', 'Fixed assets - Private', 'k1ttotl1es000', 'Billions of dollars']
        #   data_values: [(start_date_1, end_date_1, 1), (start_date_2, end_date_2, 2), .....]
        data = []
        for index, line in enumerate(lines):
            line = self.trim_ending_comma(line)
            parts = self.split_line_into_values(line)
            # Line like: Table 3.1. Government Current Receipts and Expenditures
            if len(parts) == 0:
                continue

            first_part = parts[0].strip()
            if first_part.startswith('Table'):
                first_part = first_part[5:]
                first_alpha = -1
                last_alpha = -1
                for i in range(len(first_part)):
                    if first_part[i].isalpha(): 
                        last_alpha = i
                        if first_alpha == -1:
                            first_alpha = i
                type = self.trim_ending_comma(first_part[first_alpha:last_alpha+1].strip())
                # Remove the A., B. C. crap 
                for i in range(len(type)):
                    if type[i] == ' ':
                        if type[i-1] == '.':
                            type = type[i+1:]
                        break

                unit = None
                headers = None
                quarters = None
                category_stack = []
            # Line like: [Billions of dollars; yearend estimates]
            elif parts[0].startswith('['):
                unit = parts[0].strip()[1:]
                if unit.find(']; ') > 0:
                    unit = unit.replace(']; ', ' (')
                    unit += ')'
                elif unit.find('];') > 0:
                    unit = unit.replace('];', ' (')
                    unit += ')'
                else:
                    unit = unit[:-1]
                unit = unit.replace('()', '').strip()
                type = '%s (%s)' % (type, unit)
            # Line like: Line,,,1925,1926,1927,1928,1929,1930,.....
            elif parts[0].startswith('Line'):
                headers = parts
                # Checking if the next line is the quarter line or not
                parts = self.split_line_into_values(self.trim_ending_comma(lines[index+1]))
                quarter_line_exists = True
                if (len(headers) == len(parts) and
                    parts[0] == '' and parts[1] == '' and parts[2] == ''):
                    quarters = ['', '', '']
                    for i in range(3, len(parts)):
                        try:
                            quarter = int(parts[i])
                            if quarter < 1 or quarter > 4:
                                quarter_line_exists = False
                            quarters.append(quarter)
                        except:
                            quarter_line_exists = False
                            break
                else:
                    quarter_line_exists = False

                if not quarter_line_exists:
                    quarters = None
            # Line like: 1,Fixed assets and consumer durable goods,k1wtotl1es000,296.8,307.2,....
            elif len(line) > 0 and line[0].isdigit():
                if (headers is None or
                    type is None or
                    unit is None):
                    continue
                values = parts
                try:
                    int(values[0])
                except:
                    continue
                if len(values) != len(headers):
                    logger.Logger.error('Mismatch (%d vs %d) values (%s) and headers (%s)' %(
                            len(values), len(headers), values, headers))
                    continue
                # Data line has to have id, name and name_code
                if (not values[0] or not values[1] or not values[2]):
                    continue

                data_values = []
                # WRONG WRONG WRONG quarter too, may be month too 
                for i in range(3, len(headers)):
                    try:
                        val = StringHelper.parse_value_string(values[i])
                        year = int(headers[i])
                        if year > 1800 and year < 3000 and val is not None:
                            start_date = None
                            end_date = None
                            if quarters is None:
                                start_date = datetime.datetime(year, 1, 1)
                                end_date = datetime.datetime(year+1, 1, 1)
                            elif quarters[i] == 1:
                                start_date = datetime.datetime(year, 1, 1)
                                end_date = datetime.datetime(year, 4, 1)
                            elif quarters[i] == 2:
                                start_date = datetime.datetime(year, 4, 1)
                                end_date = datetime.datetime(year, 7, 1)
                            elif quarters[i] == 3:
                                start_date = datetime.datetime(year, 7, 1)
                                end_date = datetime.datetime(year, 10, 1)
                            elif quarters[i] == 4:
                                start_date = datetime.datetime(year, 10, 1)
                                end_date = datetime.datetime(year+1, 1, 1)
                            data_values.append((start_date, end_date, val))
                    except:
                        pass
                
                # Num starting whitepsace like 2
                num_starting_whitespace = self.num_starting_whitespace(values[1])
                # Name like 'Nonresidential \2\'
                name = values[1].strip()
                if name.endswith('\\'):
                    name = name[:-1]
                    name = name[:name.rfind('\\')]
                # Name code like 'd3ntotl1es000'
                name_code = values[2].strip()
                while len(category_stack) > 0 and category_stack[-1][1] >= num_starting_whitespace:
                    category_stack.pop()
                full_name = category_stack[-1][0] + ' - ' + name if len(category_stack) > 0 else name
                full_name = full_name.strip()
                category_stack.append([full_name, num_starting_whitespace])
                data.append([type, full_name, name_code, unit, data_values])
                logger.Logger.info('Add data (%d %d) with type `%s`, full_name `%s`, name_code `%s`, unit `%s`' % (
                        index, len(lines), type, full_name, name_code, unit))
        return data

    def get_economics_info_table_name(self, economics_info):
        return 'economics_info_%d_metrics' % economics_info.id

    def insert_new_economic_info(self, data, csv_link, category):
        for line_data in data:
            type = line_data[0]
            full_name = line_data[1]
            name_code = line_data[2]
            unit = line_data[3] 
            metadata = {}
            metadata['link'] = csv_link
            metadata['name_code'] = name_code
            economics_info = EconomicsInfo(
                id=None,
                name=full_name,
                location='us',
                category=category,
                type=type,
                source='bureau_of_economic_analysis',
                metadata=json.dumps(metadata)
            )
            logger.Logger.info('Insert economic info %s %s %s %s (%s) with metadata %s' % (
                    type, full_name, name_code, unit, category, metadata))
            self.economics_info_db.insert_row(economics_info)

    def update_measures(self):
            count = 0
            while not self.q.empty():
                economics_info = self.q.get()
                count += 1
                if (count < 1000):
                    continue

                if self.daily_api_call > UpdateBureauLaborStatistics.QUOTA:
                    logger.Logger.info('Exceed daily quota of %d' % (
                            UpdateBureauLaborStatistics.QUOTA))
                    return

                logger.Logger.info(
                        '(%s) Processing economic measure %s (%s) (%s) and push to database' % (
                        threading.current_thread().name, economics_info.name,
                        economics_info.category, economics_info.type))

                self.get_time_series_data_and_update(economics_info, self.update_history)

    def update_economic_info_data(self, measure_list, csv_link, category):
        try:
            while not self.q.empty():
                line_data = self.q.get()
                type = line_data[0]
                full_name = line_data[1]
                name_code = line_data[2]
                unit = line_data[3]
                values = line_data[4]

                logger.Logger.info('Update economic info data for %s %s %s %s' % (type, full_name, name_code, unit))
                found_matching_info = False
                for economics_info in measure_list:
                    metadata = json.loads(economics_info.metadata)
                    # Found the right metrics
                    if (economics_info.name == full_name and
                        economics_info.location == 'us' and
                        economics_info.category == category and
                        economics_info.type == type and
                        metadata['link'] == csv_link and
                        metadata['name_code'] == name_code):
                        found_matching_info = True
                        tablename = self.get_economics_info_table_name(economics_info)

                        metrics_db = metrics_database.MetricsDatabase(
                                self.db_type,
                                self.username,
                                self.password,
                                self.server,
                                self.database,
                                tablename)
                        logger.Logger.info('Create metric table %s' % tablename)
                        metrics_db.create_metric()

                        # measures hold the newly-parsed data
                        metric_name = '%s (%s) (%s)' % (economics_info.name,
                                                        economics_info.category,
                                                        economics_info.type)
                        measures = []
                        for val in values:
                            try:
                                start_date = val[0]
                                end_date = val[1]
                                measure_val = val[2]
                                new_measure = metrics.Metrics(
                                        metric_name=metric_name,
                                        start_date=start_date,
                                        end_date=end_date,
                                        unit=unit,
                                        value=measure_val)
                                measures.append(new_measure)
                            except Exception as e:
                                logger.Logger.error(e)

                        logger.Logger.info('Start inserting %d values' % len(measures))
                        metrics_db.update_database_with_given_data(
                                data=measures,
                                latest_time=None,
                                earliest_time=None)
                        break
                if not found_matching_info:
                    logger.Logger.error('Cannot find matching info for %s %s %s %s' % (type, full_name, name_code, unit))
        finally:
            self.q.task_done()

    def update_measures(self):
        for category in UpdateBureauEconomicAnalysis.DATA_PAGE:
            link = UpdateBureauEconomicAnalysis.DATA_PAGE[category]
            logger.Logger.info(
                    'Processing category %s (%s) and push to database' % (category, link))

            csv_links = self.get_csv_links(link)
            logger.Logger.info('Found %d csv_links' % len(csv_links))
            for csv_link in csv_links:
                csv_content = self.get_csv_content(csv_link)
                # Data is a array. Each element is an array itself [type, full_name, name_code, unit, values]
                #   [type, full_name, name_code, unit] like [' Current-Cost Net.....', 'Fixed assets - Private', 'k1ttotl1es000', 'Billions of dollars']
                #   values: [(start_date_1, end_date_1, 1), (start_date_2, end_date_2, 2), .....]
                data = self.update_data_from_csv_content(csv_content)
                logger.Logger.info('Found %d data line' % len(data))
                for line_data in data:
                    self.q.put(line_data)
                
                # Insert entries into economics_info table first only if update_history = True
                if self.update_history:
                    self.insert_new_economic_info(data, csv_link, category)

                # Then insert data into each economics_info_#_metrics later
                measure_list = self.economics_info_db.get_economics_info_data(
                        source='bureau_of_economic_analysis')

                # Start threads to update
                threads = []
                for i in range(self.max_num_threads):
                    t = threading.Thread(target=self.update_economic_info_data, args=(measure_list, csv_link, category,))
                    threads.append(t)
                    t.start()

                for i in range(len(threads)):
                    wait_thread = threads[i]
                    logger.Logger.info('Wait for thread %s' % wait_thread.name)
                    wait_thread.join()
                    logger.Logger.info('Thread %s done' % wait_thread.name)
                
                # Sleep before download the next json
                logger.Logger.info('Sleep for %d before downloading json again' % UpdateBureauEconomicAnalysis.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)
                time.sleep(UpdateBureauEconomicAnalysis.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)


def main():
    try:
        update_obj = UpdateBureauEconomicAnalysis(
                'mysql',
                Config.mysql_username,
                Config.mysql_password,
                Config.mysql_server,
                Config.mysql_database,
                update_history=False)
        update_obj.daemon = True
        update_obj.start()
        while True:
            time.sleep(10)        
        """with open('C:\Users\hungt\Downloads\Section6All_Hist.csv', 'r') as f:
            content = f.read()
            update_obj.update_data_from_csv_content(content)
        with open('C:\Users\hungt\Downloads\Section1All_csv.csv', 'r') as f:
            content = f.read()
            update_obj.update_data_from_csv_content(content)
        with open('C:\Users\hungt\Downloads\Section3All_csv.csv', 'r') as f:
            content = f.read()
            update_obj.update_data_from_csv_content(content)"""
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
