__author__ = 'hungtantran'


from os import listdir
from os.path import isfile, join
import datetime
from ftplib import FTP

import logger
from constants_config import Config
from sec_xbrl_index_file_parser import SecXbrlIndexFileParser
from sec_file_retriever import SecFileRetriever


def retrieve_xbrl_zip_files_from_cik_list_and_xbrl_index_file(cik_list, xbrl_index_dir, intermediate_file_dir='.'):
    xbrl_index_parser = SecXbrlIndexFileParser()
    file_retriever = SecFileRetriever(link=Config.sec_ftp_link,
                                      full_index_path=Config.sec_ftp_full_index_path,
                                      xbrl_index_file=Config.sec_xbrl_index_file)
    xbrl_index_files = [join(xbrl_index_dir, f) for f in listdir(xbrl_index_dir) if (isfile(join(xbrl_index_dir, f)) and f.endswith('.idx'))]

    for xbrl_index_file in xbrl_index_files:
        # xbrl_index_file should be like path/to/index/file/2011_qtr4_xbrl.idx so
        # file_parts should be like ['2011', 'qtr4', 'xbrl.idx]
        index = xbrl_index_file.rfind('/')
        if index > 0:
            xbrl_index_file_name = xbrl_index_file[(index + 1):]
        file_parts = xbrl_index_file_name.split('_')
        if len(file_parts) != 3 or (not xbrl_index_file_name.endswith('_xbrl.idx')):
            logger.Logger.log(logger.LogLevel.WARN, 'xbrl index file has to be in format {YYYY}_qtr{Q}_xbrl.idx')
            return

        xbrl_indices = xbrl_index_parser.parse(xbrl_index_file)

        # Expect there are 5 arrays of CIK, Company Name, Form Type, Date Filed and Accession
        if len(xbrl_indices) != 5:
            return

        # Get the xbrl zip file corresponding to the company
        for i in range(len(xbrl_indices[0])):
            # Only parse 10-Q and 10-K for now
            # TODO parse more form types
            if xbrl_indices[0][i] in cik_list and (xbrl_indices[2][i] == '10-Q' or xbrl_indices[2][i] == '10-K'):
                target_file_path = '%s/%d-%s-%s-%s-%s-xbrl.zip' % (intermediate_file_dir, xbrl_indices[0][i], file_parts[0],
                                                                   file_parts[1], xbrl_indices[2][i], xbrl_indices[4][i])
                file_retriever.get_xbrl_zip_file(cik=xbrl_indices[0][i],
                                                 accession=xbrl_indices[4][i],
                                                 target_file_path=target_file_path)


cik_list=[789019]
intermediate_file_dir='./SEC/xbrl_zip_files'
xbrl_index_dir='./SEC/xbrl_index_files/'
retrieve_xbrl_zip_files_from_cik_list_and_xbrl_index_file(cik_list, xbrl_index_dir, intermediate_file_dir)