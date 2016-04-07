__author__ = 'hungtantran'

import datetime
import re
import unicodedata


class StringHelper(object):
    # TODO write unit test for this
    @staticmethod
    def clean_name(name_str):
        name_str = name_str.strip()
        name_str = name_str.replace('\n', '')
        name_str = re.sub('( )+', ' ', name_str)
        name_str = unicodedata.normalize('NFKD', name_str).encode('ascii','ignore')
        name_str = name_str.lower()
        return name_str

    # TODO write unit test for this
    @staticmethod
    def parse_value_string(value_string):
        try:
            value_string = value_string.replace(',', '')
            return float(value_string)
        except ValueError:
            return None

    @staticmethod
    def convert_datetime_to_string(datetime_obj):
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def extract_directory_and_file_name_from_path(path):
        directory = None
        file_name = None

        index = path.rfind('/')
        if index >= 0:
            file_name = path[(index + 1):]
            directory = path[:index]
        else:
            file_name = path
            directory = '.'

        return (directory, file_name)

    @staticmethod
    def convert_string_to_datetime(time_str):
        patterns = {}
        # 3/1/2016
        patterns['^[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9][0-9][0-9]$'] = '%m/%d/%Y'
        # 2016/03/03
        patterns['^[0-9][0-9][0-9][0-9]/[0-9][0-9]?/[0-9][0-9]?$'] = '%Y/%m/%d'
        # 03/04/16
        patterns['^[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9]$'] = '%m/%d/%y'
        # 2016-03-02
        patterns['^[0-9][0-9][0-9][0-9]-[0-9]+-[0-9]+$'] = '%Y-%m-%d'
        # Mar 06 2016
        patterns['^[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]? [0-9][0-9]? [0-9][0-9][0-9][0-9]$'] = '%b %d %Y'
        # Mar 06, 2016
        patterns['^[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]? [0-9][0-9]?, [0-9][0-9][0-9][0-9]$'] = '%b %d, %Y'
        # 07-Mar-2016
        patterns['^[0-9][0-9]?-[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]?-[0-9][0-9][0-9][0-9]$'] = '%d-%b-%Y'
        # 08-Mar-16
        patterns['^[0-9][0-9]?-[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]?-[0-9][0-9]$'] = '%d-%b-%y'

        for pattern in patterns:
            prog = re.compile(pattern)
            if prog.match(time_str):
                return datetime.datetime.strptime(time_str, patterns[pattern])

        return None