__author__ = 'hungtantran'


import unittest

from constants_config import Config
import logger
from generic_model_database import GenericModelDatabase


class TestGenericModelDatabase(unittest.TestCase):
    def test_create_model_with_primary_key(self):
        model_db = GenericModelDatabase('mysql',
                                         Config.test_mysql_username,
                                         Config.test_mysql_password,
                                         Config.test_mysql_server,
                                         Config.test_mysql_database)
        try:
            model_db.remove_model('TestModel')
            model_db.create_model(model='TestModel',
                                  column_names=['col1', 'col2', 'col3', 'col4'],
                                  column_types=['INTEGER', 'FLOAT', 'TEXT', 'DATETIME'],
                                  primary_key_columns=['col1', 'col2'])
            test_values = []
            test_values.append([3, 2, 'test1', '2016-03-01 00:00:00'])
            test_values.append([5, 4.0, 'test2', '2016-03-02 00:00:00'])
            test_values.append([7, 6.3, 'test3', '2016-03-03 00:00:00'])
            test_values.append([10, 9.0, None, None])
            model_db.insert_values('TestModel', test_values)

            data = model_db.get_model_data('TestModel')
            self.assertEqual(len(data), 4)

            self.assertEqual(data[0][0], 3)
            self.assertEqual(data[0][1], 2)
            self.assertEqual(data[0][2], 'test1')
            self.assertEqual(data[0][3].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')

            self.assertEqual(data[1][0], 5)
            self.assertEqual(data[1][1], 4)
            self.assertEqual(data[1][2], 'test2')
            self.assertEqual(data[1][3].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')

            self.assertEqual(data[2][0], 7)
            self.assertEqual(data[2][1], 6.3)
            self.assertEqual(data[2][2], 'test3')
            self.assertEqual(data[2][3].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-03 00:00:00')

            self.assertEqual(data[3][0], 10)
            self.assertEqual(data[3][1], 9.0)
            self.assertEqual(data[3][2], None)
            self.assertEqual(data[3][3], None)
        finally:
            model_db.remove_model('TestModel')

    def test_create_model_without_primary_key(self):
        model_db = GenericModelDatabase('mysql',
                                         Config.test_mysql_username,
                                         Config.test_mysql_password,
                                         Config.test_mysql_server,
                                         Config.test_mysql_database)
        try:
            model_db.remove_model('TestModel')
            model_db.create_model(model='TestModel',
                                  column_names=['col1', 'col2', 'col3', 'col4'],
                                  column_types=['INTEGER', 'FLOAT', 'TEXT', 'DATETIME'])
            test_values = []
            test_values.append([3, 2, 'test1', '2016-03-01 00:00:00'])
            test_values.append([5, 4.0, 'test2', '2016-03-02 00:00:00'])
            test_values.append([7, 6.3, 'test3', '2016-03-03 00:00:00'])
            model_db.insert_values('TestModel', test_values)

            data = model_db.get_model_data('TestModel')
            self.assertEqual(len(data), 3)

            self.assertEqual(data[0][0], 3)
            self.assertEqual(data[0][1], 2)
            self.assertEqual(data[0][2], 'test1')
            self.assertEqual(data[0][3].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')

            self.assertEqual(data[1][0], 5)
            self.assertEqual(data[1][1], 4)
            self.assertEqual(data[1][2], 'test2')
            self.assertEqual(data[1][3].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')

            self.assertEqual(data[2][0], 7)
            self.assertEqual(data[2][1], 6.3)
            self.assertEqual(data[2][2], 'test3')
            self.assertEqual(data[2][3].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-03 00:00:00')
        finally:
            model_db.remove_model('TestModel')


if __name__ == '__main__':
    unittest.main()


