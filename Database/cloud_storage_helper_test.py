__author__ = 'hungtantran'

import unittest
import time
import random
import os
import os.path

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
            buckets = self.storage_client.list_buckets()
            self.assertEqual(len(buckets), 4)
            self.assertEqual(buckets[0].name, 'market_data_analysis')
            self.assertEqual(buckets[1].name, 'market_data_analysis_staging')
            self.assertEqual(buckets[2].name, 'market_data_analysis_test')
            self.assertEqual(buckets[3].name, 'market_data_analysis_test_2')
        finally:
            self.tearDown()

    def test_listobjects(self):
        try:
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
            self.assertEqual(objects[2].directory, "test_dir")
            self.assertEqual(objects[2].bucket, "market_data_analysis_test")
            self.assertEqual(objects[2].is_directory, False)
            self.assertGreater(objects[2].size, 0)
        finally:
            self.tearDown()

    def test_getobject(self):
        try:
            out_filename="Database/test_files/test_data_20160511.txt"
            try:
                os.remove(out_filename)
            except Exception:
                pass

            self.assertFalse(os.path.isfile(out_filename))

            self.storage_client.get_object(
                bucket="market_data_analysis_test",
                filename="test_data_20160511.txt",
                out_filename=out_filename)

            with open(out_filename, "r") as out_file:
                self.assertEqual(out_file.read(), "test\ntest\ntest\n")
        finally:
            self.tearDown()


    def test_getdataflowobject(self):
        try:
            objects = self.storage_client.list_dataflow_result(
                    'market_data_analysis_test_2', "")
            self.assertEqual(len(objects), 1)
            self.assertEqual(objects[0].name, "result.1464158881.07.txt")
            self.assertEqual(objects[0].size, 6)
            self.assertEqual(len(objects[0].cloud_storage_objects), 6)

            for i, obj in enumerate(objects[0].cloud_storage_objects):
                self.assertEqual(
                        obj.name,
                        "result.1464158881.07.txt-0000%d-of-00006" % i)
                self.assertEqual(obj.directory, "")
                self.assertEqual(obj.bucket, "market_data_analysis_test_2")
                self.assertEqual(obj.is_directory, False)
                self.assertGreater(obj.size, 0)

            out_filename="Database/test_files/result.1464158881.07.txt"
            try:
                os.remove(out_filename)
            except Exception:
                pass
            self.storage_client.get_dataflow_object(
                    bucket="market_data_analysis_test_2",
                    dataflow_obj=objects[0],
                    out_filename=out_filename)
            with open(out_filename, "r") as out_file:
                self.assertEqual(out_file.read(), "a\nb\nc\nd\ne\nf\n")

            try:
                os.remove(out_filename)
            except Exception:
                pass
            self.storage_client.get_dataflow_file(
                    bucket="market_data_analysis_test_2",
                    dataflow_filename="result.1464158881.07.txt",
                    out_filename=out_filename)
            with open(out_filename, "r") as out_file:
                self.assertEqual(out_file.read(), "a\nb\nc\nd\ne\nf\n")
        finally:
            self.tearDown()


if __name__ == '__main__':
    unittest.main()
