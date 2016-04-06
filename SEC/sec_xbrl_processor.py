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

    def process_xbrl_zip_file(self, zip_file_path, extracted_directory='.', remove_extracted_file_after_done=False):
        logger.Logger.log(logger.LogLevel.INFO, 'Processing xbrl zip file %s' % zip_file_path)

        extracted_file_path = self.extract_xbrl_zip_file(zip_file_path=zip_file_path,
                                   extracted_directory=extracted_directory)

        results = self.parse_xbrl(xbrl_file=extracted_file_path)

        if remove_extracted_file_after_done:
            os.remove(extracted_file_path)

        return results

    def parse_xbrl(self, xbrl_file):
        logger.Logger.log(logger.LogLevel.INFO, 'Parsing xbrl file %s' % xbrl_file)

        results = {}

        try:
            tree = etree.parse(xbrl_file)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.INFO, e)
            return results

        root = tree.getroot()

        # Gather all the context informaiton.
        # key = context id
        # value = [startdate, enddate]
        context = {}
        for child in root:
            if child.tag.find('context') == -1:
                continue

            if 'id' not in child.attrib:
                continue

            context_id = child.attrib['id']

            startDate = None
            endDate = None
            for grandchild in child:
                if not grandchild.tag.endswith('period'):
                    continue

                for elem in grandchild:
                    if elem.tag.endswith('instant'):
                        startDate = elem.text
                        endDate = elem.text
                        pass
                    elif elem.tag.endswith('startDate'):
                        startDate = elem.text
                        pass
                    elif elem.tag.endswith('endDate'):
                        endDate = elem.text
                        pass

            if (startDate is not None) and (endDate is not None):
                context[context_id] = [StringHelper.convert_string_to_datetime(startDate),
                                       StringHelper.convert_string_to_datetime(endDate)]

        reverse_nsmap = {}
        for namespace in root.nsmap:
            reverse_nsmap[root.nsmap[namespace]] = namespace

        for child in root:
            try:
                full_tag = child.tag
                attrib = child.attrib
                text_value = 'a'

                if ((text_value is None) or (full_tag is None) or (attrib is None) or
                    ('unitRef' not in attrib) or ('contextRef' not in attrib) or
                    ('USD' not in attrib['unitRef']) or (attrib['contextRef'] not in context)):
                    continue

                # Each tag should look like this {http://xbrl.us/us-gaap/2009-01-31}GrossProfit
                match = re.search(r'{(.+)}(.+)', full_tag)
                if match:
                    namespace = match.group(1)
                    tag = match.group(2)
                else:
                    continue

                # If there is no namespace match this field namespace
                if namespace not in reverse_nsmap:
                    continue

                if tag not in results:
                    results[tag] = []

                context_ref = attrib['contextRef']
                # For ex: results['GrossProfit'] = [[1000, '2014-01-01', '2014-04-01', 'http://xbrl.us/us-gaap/2009-01-31']]
                results[tag].append([StringHelper.parse_value_string(child.text),
                                    context[context_ref][0],
                                    context[context_ref][1],
                                    namespace])
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, e)
            finally:
                pass

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
            return '%s/%s' % (extracted_directory, xbrl_file)
