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
                                                           year=2014,
                                                           quarter=4,
                                                           intermediate_file_dir='./SEC/test_output_files')
        self.assertGreater(len(results), 0)
        self.assertTrue('GrossProfit' in results)
        self.assertTrue('Liabilities' in results)
        self.assertTrue('Assets' in results)
        self.assertTrue('EarningsPerShareBasic' in results)
        self.assertTrue('EarningsPerShareDiluted' in results)

        self.assertEqual(len(results['Liabilities']), 2)
        self.assertEqual(results['Liabilities'][0][0], 79486000000)
        self.assertEqual(results['Liabilities'][0][1].strftime("%Y-%m-%d %H:%M:%S"), '2014-09-30 00:00:00')
        self.assertEqual(results['Liabilities'][0][2].strftime("%Y-%m-%d %H:%M:%S"), '2014-09-30 00:00:00')
        self.assertEqual(results['Liabilities'][0][3], 'http://fasb.org/us-gaap/2014-01-31')
        self.assertEqual(results['Liabilities'][1][0], 82600000000)
        self.assertEqual(results['Liabilities'][1][1].strftime("%Y-%m-%d %H:%M:%S"), '2014-06-30 00:00:00')
        self.assertEqual(results['Liabilities'][1][2].strftime("%Y-%m-%d %H:%M:%S"), '2014-06-30 00:00:00')
        self.assertEqual(results['Liabilities'][1][3], 'http://fasb.org/us-gaap/2014-01-31')

        results2 = retriever.retrieve_company_info_from_cik_and_xbrl_index_file(
            cik=789019, xbrl_index_file='./SEC/test_output_files/2014_qtr4_xbrl.idx',
            intermediate_file_dir='./SEC/test_output_files')

        self.assertGreater(len(results2), 0)
        self.assertTrue('GrossProfit' in results2)
        self.assertTrue('Liabilities' in results2)
        self.assertTrue('Assets' in results2)
        self.assertTrue('EarningsPerShareBasic' in results2)
        self.assertTrue('EarningsPerShareDiluted' in results2)

        self.assertEqual(len(results2['Liabilities']), 2)
        self.assertEqual(results2['Liabilities'][0][0], 79486000000)
        self.assertEqual(results2['Liabilities'][0][1].strftime("%Y-%m-%d %H:%M:%S"), '2014-09-30 00:00:00')
        self.assertEqual(results2['Liabilities'][0][2].strftime("%Y-%m-%d %H:%M:%S"), '2014-09-30 00:00:00')
        self.assertEqual(results2['Liabilities'][0][3], 'http://fasb.org/us-gaap/2014-01-31')
        self.assertEqual(results2['Liabilities'][1][0], 82600000000)
        self.assertEqual(results2['Liabilities'][1][1].strftime("%Y-%m-%d %H:%M:%S"), '2014-06-30 00:00:00')
        self.assertEqual(results2['Liabilities'][1][2].strftime("%Y-%m-%d %H:%M:%S"), '2014-06-30 00:00:00')
        self.assertEqual(results2['Liabilities'][1][3], 'http://fasb.org/us-gaap/2014-01-31')


if __name__ == '__main__':
    unittest.main()
