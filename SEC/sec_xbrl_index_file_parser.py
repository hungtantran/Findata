__author__ = 'hungtantran'


import logger
from generic_file_parser import GenericFileParser
from string_helper import StringHelper

class SecXbrlIndexFileParser(object):
    HEADER = 'CIK|Company Name|Form Type|Date Filed|Filename'

    def __init__(self):
        self.generic_parser = GenericFileParser()

    def parse(self, source_name):
        logger.Logger.log(logger.LogLevel.INFO, 'Parsing xbrl index file %s' % source_name)
        with open(source_name) as f:
            content = f.read()
            if SecXbrlIndexFileParser.HEADER not in content:
                return None

            content = content[content.index(SecXbrlIndexFileParser.HEADER):]
            (titles, results) = self.generic_parser.parse_content(content=content,
                                                                  delimiter='|',
                                                                  has_title=True)

            if ((len(titles) != 5) or
                (titles[0] != 'CIK') or
                (titles[1] != 'Company Name') or
                (titles[2] != 'Form Type') or
                (titles[3] != 'Date Filed') or
                (titles[4] != 'Filename')):
                return None

            num_results = len(results[0])
            for i in range(len(results)):
                if len(results[i]) != num_results:
                    return None

            # Convert cik to integer
            for i in range(len(results[0])):
                results[0][i] = int(results[0][i])

            # Convert date filed field to datetime object
            for i in range(len(results[3])):
                results[3][i] = StringHelper.convert_string_to_datetime(results[3][i])

            # Extract accession string out of filename
            for i in range(len(results[4])):
                accession = results[4][i]
                accession = accession[(accession.rfind('/') + 1):]
                accession = accession[:accession.rfind('.txt')]
                results[4][i] = accession

            return results