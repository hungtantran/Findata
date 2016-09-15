__author__ = 'hungtantran'

import init_app

import datetime
import re
from time import sleep
import sys

import logger
from dao_factory_repo import DAOFactoryRepository
from string_helper import StringHelper
from constants_config import Config


def validate_missing_economics_info():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            cursor = connection.cursor()

            query = """SHOW TABLES LIKE 'economics_info_%_metrics'"""
            cursor.execute(query)
            data = cursor.fetchall()
            tablenames = []
            for row in data:
                tablename = row[0]
                tablenames.append(tablename)

            query = "SELECT * FROM economics_info ORDER BY id"
            cursor.execute(query)
            data = cursor.fetchall()
            expected_tablenames = []
            tableinfo = {}
            for row in data:
                id = row[0]
                expected_tablenames.append('economics_info_%d_metrics' % id)
                tableinfo['economics_info_%d_metrics' % id] = row
            
            not_found_tablenames = []
            for expected_tb in expected_tablenames:
                if expected_tb not in tablenames:
                    info = tableinfo[expected_tb]
                    not_found_tablenames.append('"%s","%s","%s","%s","%s","%s","%s"' % (expected_tb, info[1], info[2], info[3], info[4], info[5], info[6]))

            with open("not_found_tablenames.csv", 'w') as f:
                f.write('\n'.join(not_found_tablenames))
            
        except Exception as e:
            print e

def validate_prefix_type_in_economics_info():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            cursor = connection.cursor()

            query = """SELECT * FROM economics_info"""
            cursor.execute(query)
            data = cursor.fetchall()
            tablenames = []
            for row in data:
                type = row[4]
                for i in range(len(type)):
                    if type[i] == ' ':
                        if type[i-1] == '.':
                            new_type = type[i+1:]
                            print type
                            print new_type
                            query2 = 'UPDATE IGNORE economics_info SET type="%s" WHERE id = %s' % (new_type, row[0])
                            print query2
                            cursor.execute(query2)
                            connection.commit()
                        break
        except Exception as e:
            print e

def validate_economics_info():
    validate_missing_economics_info()
    #validate_prefix_type_in_economics_info()
    pass


if __name__ == '__main__':
    validate_economics_info()