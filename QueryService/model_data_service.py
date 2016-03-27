__author__ = 'hungtantran'


from os import listdir
from os.path import isfile, join
import sys

from constants_config import Config
from csv_parser import CsvParser
from text_parser import TextParser
import logger
from timeline_model_database import TimelineModelDatabase


class ModelDataService(object):
    def __init__(self, db_type, username, password, server, database):
        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database

    @staticmethod
    def get_parser(file_name):
        if file_name.endswith('.csv'):
            return CsvParser()
        elif file_name.endswith('.txt'):
            return TextParser()
        else:
            return None

    def parse_and_insert_model_data_from_file(self, file_name):
        logger.Logger.log(logger.LogLevel.INFO, 'Parse and insert model data from file %s' % file_name)

        # Parse the file for content data
        parser = ModelDataService.get_parser(file_name)
        (titles, dates, results) = parser.parse(file_name)

        # Create model tables and insert the file data into the database
        model_db = TimelineModelDatabase(self.db_type, self.username, self.password,
                                         self.server, self.database)
        for i in range(len(titles)):
            title = titles[i]
            model_db.create_model(title)

            for j in range(len(dates)):
                date = dates[j]
                value = results[i][j]
                model_db.insert_value(title, date, value)

    def parse_and_insert_model_data_from_directory(self, dir_name):
        logger.Logger.log(logger.LogLevel.INFO, 'Parse and insert model data from directory %s' % dir_name)

        file_names = [join(dir_name, f) for f in listdir(dir_name) if isfile(join(dir_name, f))]
        for file_name in file_names:
            self.parse_and_insert_model_data_from_file(file_name)


def main():
    args = sys.argv

    model_data_service = ModelDataService('mysql',
                                          Config.mysql_username,
                                          Config.mysql_password,
                                          Config.mysql_server,
                                          Config.mysql_database)
    model_data_service.parse_and_insert_model_data_from_directory('.\\Common\\test_files\\')

    for i in range(1, len(args)):
        arg = args[i]
        if arg.startsWith('directories='):
            dir_str = arg[len('directories='):]
            dirs = dir_str.split(',')
            for dir_name in dirs:
                model_data_service.parse_and_insert_model_data_from_directory(dir_name)
        elif arg.startsWith('files='):
            file_str = arg[len('files='):]
            files = file_str.split(',')
            for file_name in files:
                model_data_service.parse_and_insert_model_data_from_file(file_name)

if __name__ == '__main__':
    main()