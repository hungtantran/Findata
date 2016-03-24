__author__ = 'hungtantran'

import unittest

import logger
from daofactoryrepo import DAOFactoryRepository


class TestMysqlDAOFactory(unittest.TestCase):
    def test_createdb(self):
        mysql_dao_factory = DAOFactoryRepository.getInstance('mysql')
        mysql_connection = mysql_dao_factory.create('root', 'amazonebay1', '104.154.40.63', 'models')
        mysql_cursor = mysql_connection.cursor()
        mysql_cursor.execute("SELECT VERSION()")
        data = mysql_cursor.fetchone()

        logger.Logger.log(logger.LogLevel.INFO, 'Mysql version %s' % data)
        self.assertGreater(len(data), 0)
        mysql_connection.close()


if __name__ == '__main__':
    unittest.main()