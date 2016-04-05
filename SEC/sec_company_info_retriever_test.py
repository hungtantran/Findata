__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from sec_company_info_retriever import SecCompanyInfoRetriever


class TestSecCompanyInfoRetriever(unittest.TestCase):
    def test_retrieve_company_info_from_cik(self):
        retriever = SecCompanyInfoRetriever()
        results = retriever.retrieve_company_info_from_cik(cik=789019,
                                                           field_tags=Config.sec_field_tags,
                                                           year=2014,
                                                           quarter=4,
                                                           intermediate_file_dir='./SEC/test_output_files')

        for tag in Config.sec_field_tags:
            self.assertGreater(len(results[tag]), 0)

        results2 = retriever.retrieve_company_info_from_cik_and_xbrl_index_file(
            cik=789019, field_tags=Config.sec_field_tags, xbrl_index_file='./SEC/test_output_files/2014_qtr4_xbrl.idx',
            intermediate_file_dir='./SEC/test_output_files')
        for tag in Config.sec_field_tags:
            self.assertGreater(len(results2[tag]), 0)


if __name__ == '__main__':
    unittest.main()
