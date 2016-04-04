__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from sec_xbrl_processor import SecXbrlProcessor


class TestSecXbrlProcessor(unittest.TestCase):
    def test_extract_xbrl_zip_file(self):
        processor = SecXbrlProcessor()
        target_directory = './SEC/test_output_files'
        target_file_path = "%s/msft-20140930.xml" % target_directory
        zip_file_path = './SEC/test_files/microsoft_2014_QTR4_10-Q.zip'

        try:
            os.remove(target_file_path)
        except Exception:
            pass

        processor.extract_xbrl_zip_file(zip_file_path=zip_file_path,
                                        extracted_directory=target_directory)

        with open(target_file_path, 'r') as file:
            self.assertTrue(filecmp.cmp(target_file_path, './SEC/test_files/msft-20140930.xml'))

    def test_parse_xbrl(self):
        xbrl_file = './SEC/test_files/msft-20140930.xml'

        processor = SecXbrlProcessor()

        field_tags = ['us-gaap:GrossProfit', 'us-gaap:fake', 'fake']
        results = processor.parse_xbrl(xbrl_file, field_tags)

        self.assertEqual(len(field_tags), len(results))
        self.assertEqual(results['us-gaap:GrossProfit'], 13384000000)
        self.assertIsNone(results['us-gaap:fake'])
        self.assertIsNone(results['fake'])


if __name__ == '__main__':
    unittest.main()
