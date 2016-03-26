__author__ = 'hungtantran'


from os import listdir
from os.path import isfile, join

from csv_parser import CsvParser
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
