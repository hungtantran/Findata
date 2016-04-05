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

    def retrieve_company_info_from_cik(self, cik, field_tags, year, quarter):
        results = {}
        if (cik is None or
            field_tags is None or
            year is None or
            quarter is None):
            return results

        # Get the xbrl index file and parse it
        xbrl_file_path = self.file_retriever.get_past_xbrl_index(year=year, quarter=quarter)
        xbrl_indices = self.xbrl_index_parser.parse(xbrl_file_path)

        # Expect there are 5 arrays of CIK, Company Name, Form Type, Date Filed and Accession
        if len(xbrl_indices) != 5:
            return results

        # Get the xbrl zip file corresponding to the company
        xbrl_zip_file = None
        for i in range(len(xbrl_indices[0])):
            if xbrl_indices[0][i] == cik:
                xbrl_zip_file = self.file_retriever.get_xbrl_zip_file(cik=cik,
                                                                      accession=xbrl_indices[4][i])
                break

        if xbrl_zip_file is None:
            return results

        # Extract the xbrl zip file, get the information file and parse it
        return self.xbrl_processor.process_xbrl_zip_file(zip_file_path=xbrl_zip_file,
                                                         field_tags=field_tags)

    def retrieve_companies_info_from_cik(self, cik_list, field_tags, year, quarter):
        pass

    def retrieve_company_info_from_ticker(self, ticker, field_tags, year, quarter):
        pass

    def retrive_companies_info_from_ticker(self, ticker_list, field_tags, year, quarter):
        pass