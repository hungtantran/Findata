__author__ = 'hungtantran'


import os
import re
import zipfile
from lxml import etree

import logger
from string_helper import StringHelper


class SecXbrlProcessor(object):
    XBRL_FILE_PATTERN = '^[a-zA-Z]+-[0-9]+\.xml'

    def __init__(self):
        pass

    def process_xbrl_zip_file(self, zip_file_path, extracted_directory='.', remove_extracted_file_after_done=True):
        self.extract_xbrl_zip_file(zip_file_path=zip_file_path,
                                   extracted_directory=extracted_directory)

        extracted_file_path = '%s/%s' % (extracted_directory, zip_file_path)
        with open(extracted_file_path) as file:
            content = file.read()

        if remove_extracted_file_after_done:
            os.remove(extracted_file_path)

    def parse_xbrl(self, xbrl_file, field_tags):
        tree = etree.parse(xbrl_file)
        root = tree.getroot()

        results = {}
        for tag in field_tags:
            results[tag] = None

            index = tag.find(':')
            if index < 0:
                continue

            namespace = tag[:index]
            if namespace in root.nsmap:
                namespace = root.nsmap[namespace]

            field_name = tag[(index + 1):]
            full_field_tag = '{%s}%s' % (namespace, field_name)
            print full_field_tag
            elem = root.find(full_field_tag)

            if elem is not None:
                results[tag] = StringHelper.parse_value_string(elem.text)


        return results

    def extract_xbrl_zip_file(self, zip_file_path, extracted_directory='.'):
        if not zipfile.is_zipfile(zip_file_path):
            logger.Logger.log(logger.LogLevel.WARN, 'Give file %s is not zip file' % zip_file_path)
            return None

        with zipfile.ZipFile(zip_file_path) as zip_file:
            files = zip_file.namelist()
            prog = re.compile(SecXbrlProcessor.XBRL_FILE_PATTERN)

            xbrl_file = None
            for file in files:
                if prog.match(file):
                    logger.Logger.log(logger.LogLevel.INFO, 'Found xbrl file %s' % file)
                    xbrl_file = file
                    break

            if xbrl_file is None:
                logger.Logger.log(logger.LogLevel.WARN, 'Cannot find any xbrl file in zip %s. Found these files %s' % (
                        zipfile, files))

            zip_file.extract(xbrl_file, extracted_directory)
