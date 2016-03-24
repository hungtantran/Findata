__author__ = 'hungtantran'

import MySQLdb
from daofactory import DAOFactory


class MysqlDAOFactory(DAOFactory):
    @staticmethod
    def create(username, password, server, database):
        return MySQLdb.connect(server, username, password, database)