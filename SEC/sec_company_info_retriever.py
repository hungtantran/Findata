__author__ = 'hungtantran'


import logger
from constants_config import Config
from sec_xbrl_processor import SecXbrlProcessor
from sec_file_retriever import SecFileRetriever
from sec_xbrl_index_file_parser import SecXbrlIndexFileParser


class SecCompanyInfoRetriever(object):
    def __init__(self):
        self.file_retriever = SecFileRetriever(link=Config.sec_ftp_link,
                                               full_index_path=Config.sec_ftp_full_index_path,
                                               xbrl_index_file=Config.sec_xbrl_index_file)
        self.xbrl_processor = SecXbrlProcessor()
        self.xbrl_index_parser = SecXbrlIndexFileParser()

    def retrieve_company_info_from_cik(self, cik, year, quarter, intermediate_file_dir='.'):
        logger.Logger.log(logger.LogLevel.INFO,
                          'Retrieve company info with cik %d, year %d, quarter %d' % (cik, year, quarter))
        results = {}
        if (cik is None or
            year is None or
            quarter is None):
            return results

        # Get the xbrl index file and parse it
        xbrl_index_file = self.file_retriever.get_past_xbrl_index(year=year,
                                                                  quarter=quarter,
                                                                  target_dir=intermediate_file_dir)

        return self.retrieve_company_info_from_cik_and_xbrl_index_file(cik=cik,
                                                                       xbrl_index_file=xbrl_index_file,
                                                                       intermediate_file_dir=intermediate_file_dir)

    def retrieve_company_info_from_cik_and_xbrl_index_file(self, cik, xbrl_index_file, intermediate_file_dir='.'):
        logger.Logger.log(logger.LogLevel.INFO,
                          'Retrieve company info with cik %d, xbrl_index_file %s' % (cik, xbrl_index_file))
        results = {}

        # xbrl_index_file should be like path/to/index/file/2011_qtr4_xbrl.idx so
        # file_parts should be like ['2011', 'qtr4', 'xbrl.idx]
        index = xbrl_index_file.rfind('/')
        if index > 0:
            xbrl_index_file_name = xbrl_index_file[(index + 1):]
        file_parts = xbrl_index_file_name.split('_')
        if len(file_parts) != 3 or (not xbrl_index_file_name.endswith('_xbrl.idx')):
            logger.Logger.log(logger.LogLevel.WARN, 'xbrl index file has to be in format {YYYY}_qtr{Q}_xbrl.idx')
            return results

        xbrl_indices = self.xbrl_index_parser.parse(xbrl_index_file)

        # Expect there are 5 arrays of CIK, Company Name, Form Type, Date Filed and Accession
        if len(xbrl_indices) != 5:
            return results

        # Get the xbrl zip file corresponding to the company
        xbrl_zip_file = None
        for i in range(len(xbrl_indices[0])):
            # Only parse 10-Q and 10-K for now
            # TODO parse more form types
            if xbrl_indices[0][i] == cik and (xbrl_indices[2][i] == '10-Q' or xbrl_indices[2][i] == '10-K'):
                target_file_path = '%s/%d-%s-%s-%s-%s-xbrl.zip' % (intermediate_file_dir, cik, file_parts[0],
                                                                   file_parts[1], xbrl_indices[2][i],
                                                                   xbrl_indices[4][i])
                xbrl_zip_file = self.file_retriever.get_xbrl_zip_file(cik=cik,
                                                                      accession=xbrl_indices[4][i],
                                                                      target_file_path=target_file_path)
                break

        if xbrl_zip_file is None:
            return results

        # Extract the xbrl zip file, get the information file and parse it
        return self.xbrl_processor.process_xbrl_zip_file(zip_file_path=xbrl_zip_file,
                                                         extracted_directory=intermediate_file_dir)

    def retrieve_companies_info_from_cik(self, cik_list, year, quarter):
        pass

    def retrieve_company_info_from_ticker(self, ticker, year, quarter):
        pass

    def retrive_companies_info_from_ticker(self, ticker_list, year, quarter):
        pass