__author__ = 'hungtantran'

import unittest
import time
import random

from constants_config import Config
import logger
from dao_factory_repo import DAOFactoryRepository


class TestBigqueryDAOFactory(unittest.TestCase):
    def test_createdroptable(self):
        bigquery_dao_factory = DAOFactoryRepository.getInstance('bigquery')
        bigquery_connection = bigquery_dao_factory.create(Config.test_bigquery_username,
                                                          Config.test_bigquery_password,
                                                          Config.test_bigquery_server,
                                                          Config.test_bigquery_database)
        bigquery_cursor = bigquery_connection.cursor()

        try:
            bigquery_cursor.delete_table('TEST1')
            bigquery_cursor.delete_table('TEST2')
            bigquery_cursor.execute("CREATE TABLE TEST1 (FIRST_NAME CHAR(20) NOT NULL, id INT, value FLOAT)")
            bigquery_cursor.execute("CREATE TABLE TEST2 (FIRST_NAME STRING, id INTEGER, value FLOAT, time DATETIME)")
            tables = bigquery_cursor.list_table()
            self.assertEqual(2, len(tables))
            self.assertEqual("TEST1", tables[0])
            self.assertEqual("TEST2", tables[1])
        finally:
            bigquery_cursor.delete_table('TEST1')
            bigquery_cursor.delete_table('TEST2')

    def test_insert_select(self):
        bigquery_dao_factory = DAOFactoryRepository.getInstance('bigquery')
        bigquery_connection = bigquery_dao_factory.create(Config.test_bigquery_username,
                                                          Config.test_bigquery_password,
                                                          Config.test_bigquery_server,
                                                          Config.test_bigquery_database)
        bigquery_cursor = bigquery_connection.cursor()

        try:
            # Be careful:
            # http://stackoverflow.com/questions/19131313/bigquery-error-500-on-streaming-insert-via-java-api/19145783#19145783
            rand_tablename = 'TEST' + str(random.randint(1, 1000))
            bigquery_cursor.delete_table(rand_tablename)
            bigquery_cursor.execute("CREATE TABLE %s (FIRST_NAME STRING, id INTEGER, value FLOAT, time DATETIME)" % rand_tablename)

            values = []
            values.append(['test1', 2, 3, '2016-03-07 00:00:00'])
            values.append(['test2', 4, 5.5, '2016-03-08 00:00:00'])
            values.append(['test3', 6, 7.8, '2016-03-09 00:00:00'])
            bigquery_cursor.insert(rand_tablename, values)
            results = bigquery_cursor.query('SELECT * FROM %s' % rand_tablename)
        finally:
            #bigquery_cursor.delete_table(rand_tablename)
            pass


if __name__ == '__main__':
    unittest.main()