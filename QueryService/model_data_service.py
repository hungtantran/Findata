__author__ = 'hungtantran'


from csv_parser import CsvParser
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

    def parse_and_insert_model_data(self, file_name):
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