__author__ = 'hungtantran'

import MySQLdb
from dao_factory import DAOFactory


class MysqlDAOFactory(DAOFactory):
    @staticmethod
    def create(username, password, server, database):
        return MysqlConnection(MySQLdb.connect(server, username, password, database))


class MysqlConnection(MySQLdb.connection):
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def cursor(self):
        return self.connection.cursor()