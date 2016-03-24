__author__ = 'hungtantran'

import unittest

import logger
from daofactoryrepo import DAOFactoryRepository


class TestMysqlDAOFactory(unittest.TestCase):
    username = 'root'
    password = 'test'
    server = '104.154.40.63'
    database = 'models'

    def test_connection(self):
        mysql_dao_factory = DAOFactoryRepository.getInstance('mysql')
        with mysql_dao_factory.create(TestMysqlDAOFactory.username,
                                      TestMysqlDAOFactory.password,
                                      TestMysqlDAOFactory.server,
                                      TestMysqlDAOFactory.database) as mysql_connection:
            mysql_cursor = mysql_connection.cursor()
            mysql_cursor.execute("SELECT VERSION()")
            data = mysql_cursor.fetchone()

            logger.Logger.log(logger.LogLevel.INFO, 'Mysql version %s' % data)
            self.assertGreater(len(data), 0)

    def test_createtable(self):
        mysql_dao_factory = DAOFactoryRepository.getInstance('mysql')
        with mysql_dao_factory.create(TestMysqlDAOFactory.username,
                                      TestMysqlDAOFactory.password,
                                      TestMysqlDAOFactory.server,
                                      TestMysqlDAOFactory.database) as mysql_connection:
            mysql_cursor = mysql_connection.cursor()
            mysql_cursor.execute("DROP TABLE IF EXISTS TEST1")
            mysql_cursor.execute("CREATE TABLE TEST1 (FIRST_NAME  CHAR(20) NOT NULL)")
            mysql_cursor.execute("SHOW TABLES LIKE 'TEST1'")

            table = mysql_cursor.fetchone()
            self.assertEqual(1, len(table))
            self.assertEqual("TEST1", table[0])

if __name__ == '__main__':
    unittest.main()