__author__ = 'hungtantran'

import unittest
import time
import random

from constants_config import Config
import logger
from cloud_sql_helper import CloudSqlHelper


class TestCloudSqlHelper(unittest.TestCase):
    def setUp(self):
        self.cloud_sql_client = CloudSqlHelper(
                project_id=Config.cloud_projectid,
                instance_id=Config.cloudsql_instanceid,
                client_secret=Config.cloudsql_secret_json)

    def tearDown(self):
        pass

    def test_listbuckets(self):
        try:
            self.setUp()
            self.cloud_sql_client.list_instances()
        finally:
            self.tearDown()



if __name__ == '__main__':
    unittest.main()
