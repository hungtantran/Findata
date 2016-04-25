__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from database_analytic import DatabaseAnalytic
from generic_model_database import GenericModelDatabase


class TestDatabaseAnalytic(unittest.TestCase):
    @staticmethod
    def analytic_function(data):
        sum = 0
        for row in data:
            sum += row[0]
        return sum

    def test_create_model_with_primary_key(self):
        model_db = GenericModelDatabase(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database)
        try:
            for i in range(5):
                tablename = 'test%d' % i
                model_db.remove_model(tablename)
                model_db.create_model(
                        model=tablename,
                        column_names=['col1', 'col2'],
                        column_types=['INTEGER', 'FLOAT'],
                        primary_key_columns=['col1'])

                test_values = []
                for j in range(5):
                    test_values.append([i * 10 + j, i * 10 + j + 1])
                model_db.insert_values(tablename, test_values)

            analytics = DatabaseAnalytic(
                    'mysql',
                    Config.test_mysql_username,
                    Config.test_mysql_password,
                    Config.test_mysql_server,
                    Config.test_mysql_database).\
                    LimitTableNames(['test1','test2','test3']).\
                    QueryTableName('test1|test3').\
                    Filter('MOD(col1, 2) = 0').\
                    Fields(['col1', 'col1']).\
                    LimitResultPerTable(5).\
                    AnalyticFunc(analytic_func=TestDatabaseAnalytic.analytic_function)
            analytics.RunAnalytic()
            results = analytics.GetAnalyticResults()
            self.assertEquals(len(results), 2)
            self.assertEquals(results['test1'], 36)
            self.assertEquals(results['test3'], 96)
        finally:
            for i in range(5):
                tablename = 'test%d' % i
                model_db.remove_model(tablename)
                pass


if __name__ == '__main__':
    unittest.main()


