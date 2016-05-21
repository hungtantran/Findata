__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from sec_file_retriever import SecFileRetriever


class TestSecFileRetriever(unittest.TestCase):
    def test_get_latest_xbrl_index(self):
        file_retriver = SecFileRetriever(link=Config.sec_ftp_link,
                                         full_index_path=Config.sec_ftp_full_index_path)
        target_file_path = "%s/latest_%s" % ('./SEC/test_output_files', Config.sec_xbrl_index_file)

        try:
            os.remove(target_file_path)
        except Exception:
            pass

        file_retriver.get_latest_xbrl_index(target_dir='./SEC/test_output_files')

        with open(target_file_path, 'r') as file:
            content = file.read()
            self.assertGreater(len(content), 0)
            self.assertTrue('CIK|Company Name|Form Type|Date Filed|Filename' in content)

    def test_get_past_xbrl_index(self):
        file_retriver = SecFileRetriever(link=Config.sec_ftp_link,
                                         full_index_path=Config.sec_ftp_full_index_path)
        target_file_path = "%s/2014_QTR4_%s" % ('./SEC/test_output_files', Config.sec_xbrl_index_file)

        try:
            os.remove(target_file_path)
        except Exception:
            pass

        file_retriver.get_past_xbrl_index(year=2014,
                                          quarter=4,
                                          target_dir='./SEC/test_output_files')

        with open(target_file_path, 'r') as file:
            content = file.read()
            self.assertGreater(len(content), 0)
            self.assertTrue('CIK|Company Name|Form Type|Date Filed|Filename' in content)

    def test_get_xbrl_zip_file(self):
        file_retriver = SecFileRetriever(link=Config.sec_ftp_link,
                                         full_index_path=Config.sec_ftp_full_index_path)
        target_file_path = "%s/microsoft_2014_QTR4_10-Q.zip" % './SEC/test_output_files'

        try:
            os.remove(target_file_path)
        except Exception:
            pass

        file_retriver.get_xbrl_zip_file(789019, '0001193125-14-380252', target_file_path)

        self.assertTrue(filecmp.cmp(target_file_path, './SEC/test_files/microsoft_2014_QTR4_10-Q.zip'))

    def test_get_file(self):
        file_retriver = SecFileRetriever(link=Config.sec_ftp_link,
                                         full_index_path=Config.sec_ftp_full_index_path)
        target_file_path = "%s/sample_xbrl_file.txt" % './SEC/test_output_files'

        try:
            os.remove(target_file_path)
        except Exception:
            pass

        file_retriver.get_file(ftp_file_path='edgar/data/1027596/0000894189-16-008706.txt',
                               target_file_path=target_file_path)

        with open(target_file_path, 'r') as file:
            content = file.read()
            self.assertGreater(len(content), 0)


if __name__ == '__main__':
    unittest.main()
