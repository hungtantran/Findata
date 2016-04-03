__author__ = 'hungtantran'


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


if __name__ == '__main__':
    unittest.main()
