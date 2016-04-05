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

        field_tags = ['us-gaap:Liabilities', 'us-gaap:fake', 'fake']
        results = processor.parse_xbrl(xbrl_file, field_tags)

        self.assertEqual(len(field_tags), len(results))
        self.assertEqual(0, len(results['us-gaap:fake']))
        self.assertEqual(0, len(results['fake']))

        self.assertEqual(len(results['us-gaap:Liabilities']), 2)
        self.assertEqual(results['us-gaap:Liabilities'][0][0], 79486000000)
        self.assertEqual(results['us-gaap:Liabilities'][0][1].strftime("%Y-%m-%d %H:%M:%S"), '2014-09-30 00:00:00')
        self.assertEqual(results['us-gaap:Liabilities'][0][2].strftime("%Y-%m-%d %H:%M:%S"), '2014-09-30 00:00:00')
        self.assertEqual(results['us-gaap:Liabilities'][1][0], 82600000000)
        self.assertEqual(results['us-gaap:Liabilities'][1][1].strftime("%Y-%m-%d %H:%M:%S"), '2014-06-30 00:00:00')
        self.assertEqual(results['us-gaap:Liabilities'][1][2].strftime("%Y-%m-%d %H:%M:%S"), '2014-06-30 00:00:00')


if __name__ == '__main__':
    unittest.main()
