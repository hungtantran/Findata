__author__ = 'hungtantran'

import datetime
import re
import urllib
import time
import threading
from bs4 import BeautifulSoup

import logger
import metrics
import ticker_info
import metrics_database
import ticker_info_database
from string_helper import StringHelper
from Common.constants_config import Config


class UpdateSecCompanyNameCikSic(threading.Thread):
    WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC = 1
    SEC_CIK_LINKS = [
        'https://www.sec.gov/divisions/corpfin/organization/cfia-123.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-a.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-b.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-c.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-d.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-e.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-f.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-g.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-h.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-i.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-j.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-k.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-l.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-m.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-n.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-o.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-p.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-q.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-r.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-s.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-t.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-uv.htm',
        'https://www.sec.gov/divisions/corpfin/organization/cfia-wxyz.htm'
    ]


    def __init__(self, db_type, username, password, server, database):
        threading.Thread.__init__(self)

        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.ticker_info_db = ticker_info_database.TickerInfoDatabase(db_type, username, password, server, database)
        self.data = None
        self.existing_data = None
        self.update_frequency_seconds = 43200

    def run(self):
        while True:
            self.existing_data = self.ticker_info_db.get_ticker_info_data()

            for link in UpdateSecCompanyNameCikSic.SEC_CIK_LINKS:
                self.clear_data()
                self.data = []

                self.update_company_name_cik_sic(link)
                self.update_database()
                logger.Logger.log(logger.LogLevel.INFO, 'Sleep for %d secs before updating again' %
                                  UpdateSecCompanyNameCikSic.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)
                time.sleep(UpdateSecCompanyNameCikSic.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)

            logger.Logger.log(logger.LogLevel.INFO,
                              'Sleep for %d secs before updating again' % self.update_frequency_seconds)
            # TODO make it sleep through weekend
            time.sleep(self.update_frequency_seconds)

    def clear_data(self):
        self.data = None

    def update_company_name_cik_sic(self, link):
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Update ticker_info with link %s now' % link)
            response = urllib.urlopen(link)
            html_string = response.read()
            return self.update_from_html_content(html_string)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def _get_content_table(self, html_elem):
        content_table_elem = html_elem.findAll('table', attrs={'id': 'cos'})
        if len(content_table_elem) != 1:
            logger.Logger.log(logger.LogLevel.ERROR, 'Found %d content table' % len(content_table_elem))
            return None

        return content_table_elem[0]

    def update_from_html_content(self, html_string):
        try:
            html_elem = BeautifulSoup(html_string, 'html.parser')

            # Get the table html elem
            content_table_elem = self._get_content_table(html_elem)
            if content_table_elem is None:
                logger.Logger.log(logger.LogLevel.WARN, 'Exit found no content table')
                return

            rows_elem = content_table_elem.findAll('tr', attrs={'valign': 'top'})
            if len(rows_elem) == 0:
                logger.Logger.log(logger.LogLevel.INFO, 'Exit found no row values left')
                return

            # Iterate through each row in the table, extract date and value
            for i in range(len(rows_elem)):
                row_elem = rows_elem[i]
                tds_elem = row_elem.findAll('td')

                if len(tds_elem) != 3:
                    logger.Logger.log(logger.LogLevel.WARN, 'Found row with %d cells (expect 3)' % len(tds_elem))
                    continue

                try:
                    self.data.append([
                        tds_elem[0].get_text().lower(),
                        int(tds_elem[1].get_text()),
                        int(tds_elem[2].get_text())]
                    )
                except:
                    logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)        

        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def update_database(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Update database ticker_info')
        self._update_database_with_given_data(self.data, self.existing_data)

    def new_row_match_existing_row(self, row, existing_row):
        if existing_row.name is None:
            return False

        # If the names match exactly, they are the same
        sanitize_name = StringHelper.remove_all_non_space_non_alphanumeric(row[0])
        sanitize_existing_name = StringHelper.remove_all_non_space_non_alphanumeric(existing_row.name.lower())

        if sanitize_name == sanitize_existing_name:
            if ((existing_row.cik is None or row[1] != existing_row.cik) or
                (existing_row.sic is None or row[2] != existing_row.sic)):
                logger.Logger.log(logger.LogLevel.INFO, 'Updating "%s" for (cik, sic) from (%s, %s) to (%s, %s)' % (
                        existing_row.name, existing_row.cik, existing_row.sic, row[1], row[2]))

                existing_row.cik = row[1]
                existing_row.sic = row[2]
                return True

        # TODO expand the selection criteria to more than just exact string match

        return False

    def _update_database_with_given_data(self, data, existing_data):
        logger.Logger.log(logger.LogLevel.INFO, 'Update database ticker_info with given data')

        num_value_update = 0
        for row in data:
            for existing_row in existing_data:
                if self.new_row_match_existing_row(row, existing_row):
                    self.ticker_info_db.update_row(existing_row)
                    num_value_update += 1

        logger.Logger.log(logger.LogLevel.INFO,
                          'Update table ticker_info with ticker_info with %d new values' % (num_value_update))


def main():
    try:
        update_obj = UpdateSecCompanyNameCikSic(
                'mysql',
                Config.mysql_username,
                Config.mysql_password,
                Config.mysql_server,
                Config.mysql_database)
        update_obj.daemon = True
        update_obj.start()

        while True:
            time.sleep(1)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
