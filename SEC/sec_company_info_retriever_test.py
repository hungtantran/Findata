__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from sec_company_info_retriever import SecCompanyInfoRetriever


class TestSecCompanyInfoRetriever(unittest.TestCase):
    def test_extract_xbrl_zip_file(self):
        retriever = SecCompanyInfoRetriever()
        results = retriever.retrieve_company_info_from_cik(cik=789019,
                                                           field_tags=Config.sec_field_tags,
                                                           year=2014,
                                                           quarter=4)

        for tag in Config.sec_field_tags:
            self.assertGreater(len(results[tag]), 0)


if __name__ == '__main__':
    unittest.main()
