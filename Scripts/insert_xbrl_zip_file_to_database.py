__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from sec_xbrl_processor import SecXbrlProcessor
from sec_xbrl_database_helper import SecXbrlDatabaseHelper
from sec_ticker_info_helper import SecTickerInfoHelper


def process_xbrl_directory_and_push_database(xbrl_zip_directory, extracted_directory):
    sec_xbrl_database_helper = SecXbrlDatabaseHelper('mysql',
                                                              Config.mysql_username,
                                                              Config.mysql_password,
                                                              Config.mysql_server,
                                                              Config.mysql_database)
    ticker_info_helper = SecTickerInfoHelper('mysql',
                                                  Config.mysql_username,
                                                  Config.mysql_password,
                                                  Config.mysql_server,
                                                  Config.mysql_database)
    processor = SecXbrlProcessor()

    try:
        processor.process_xbrl_directory_and_push_database(xbrl_zip_directory=xbrl_zip_directory,
                                                           sec_xbrl_database_helper=sec_xbrl_database_helper,
                                                           sec_ticker_info_helper=ticker_info_helper,
                                                           extracted_directory=extracted_directory,
                                                           remove_extracted_file_after_done=False)
    except Exception as e:
        print e


#process_xbrl_directory_and_push_database(xbrl_zip_directory='SEC/xbrl_zip_files',
#                                         extracted_directory='SEC/xbrl_output_files')
