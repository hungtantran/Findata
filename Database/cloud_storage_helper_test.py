__author__ = 'hungtantran'

import unittest
import time
import random

from constants_config import Config
import logger
from cloud_storage_helper import CloudStorageHelper


class TestCloudStorageHelper(unittest.TestCase):
    def setUp(self):
        self.storage_client = CloudStorageHelper(
                project_id=Config.cloud_projectid,
                client_secret=Config.cloudstorage_secret_json)

    def tearDown(self):
        pass

    def test_listbuckets(self):
        try:
            self.setUp()
            buckets = self.storage_client.list_buckets()
            self.assertEqual(len(buckets), 3)
            self.assertEqual(buckets[0].name, 'market_data_analysis')
            self.assertEqual(buckets[1].name, 'market_data_analysis_staging')
            self.assertEqual(buckets[2].name, 'market_data_analysis_test')
        finally:
            self.tearDown()


    def test_listobjects(self):
        try:
            self.setUp()
            objects = self.storage_client.list_objects(
                    'market_data_analysis_test',
                    'test_data_20160511.txt')
            self.assertEqual(len(objects), 1)
            self.assertEqual(objects[0].name, "test_data_20160511.txt")
            self.assertEqual(objects[0].directory, "")

            objects = self.storage_client.list_objects(
                    'market_data_analysis_test',
                    None)
            self.assertEqual(len(objects), 3)

            self.assertEqual(objects[0].name, "test_data_20160511.txt")
            self.assertEqual(objects[0].directory, "")
            self.assertEqual(objects[0].bucket, "market_data_analysis_test")
            self.assertEqual(objects[0].is_directory, False)
            self.assertGreater(objects[0].size, 0)

            self.assertEqual(objects[1].name, "test_dir")
            self.assertEqual(objects[1].directory, "")
            self.assertEqual(objects[1].bucket, "market_data_analysis_test")
            self.assertEqual(objects[1].is_directory, True)
            self.assertEqual(objects[1].size, 0)

            self.assertEqual(objects[2].name, "result.txt")
            self.assertEqual(objects[2].directory, "test_dir/")
            self.assertEqual(objects[2].bucket, "market_data_analysis_test")
            self.assertEqual(objects[2].is_directory, False)
            self.assertGreater(objects[2].size, 0)
        finally:
            self.tearDown()

    def test_getobject(self):
        try:
            self.setUp()

            out_filename="Database/test_files/test_data_20160511.txt"
            with open(out_filename, "w") as out_file:
                self.storage_client.get_object(
                        bucket="market_data_analysis_test",
                        filename="test_data_20160511.txt",
                        out_file=out_file)
        finally:
            self.tearDown()


if __name__ == '__main__':
    unittest.main()
