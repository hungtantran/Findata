__author__ = 'hungtantran'


import re
import unicodedata


class StringHelper(object):
    @staticmethod
    def clean_name(name_str):
        name_str = name_str.strip()
        name_str = name_str.replace('\n', '')
        name_str = re.sub('( )+', ' ', name_str)
        name_str = unicodedata.normalize('NFKD', name_str).encode('ascii','ignore')
        name_str = name_str.lower()
        return name_str

    @staticmethod
    def parse_value_string(value_string):
        try:
            value_string = value_string.replace(',', '')
            return float(value_string)
        except ValueError:
            return None