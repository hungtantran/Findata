__author__ = 'hungtantran'


import os
import re
import zipfile
import json
from lxml import etree

import logger
import Queue
import threading
from string_helper import StringHelper
from sec_xbrl_helper import SecXbrlHelper
from sec_ticker_info_helper import SecTickerInfoHelper
from sec_xbrl_database_helper import SecXbrlDatabaseHelper


class SecXbrlProcessor(object):
    XBRL_FILE_PATTERN = '^[a-zA-Z]+-[0-9]+\.xml'
    MAX_PROCESSING_THREADS = 10

    def __init__(self):
        self.q = Queue.Queue()

    @staticmethod
    def parse_xbrl_zip_file_name(xbrl_zip_file_name):
        # TODO extend more than just 10Q, 10K
        # The zip file name should look like this msft-51143-2009-qtr3-10-Q-0001104659-09-045198-xbrl.zip
        match = re.search(r"([a-zA-Z]+)-(\d+)-(\d+)-qtr(\d)-(10-Q|10-K)-.+", xbrl_zip_file_name)
        if match:
            # Return ticker, cik, year, quarter, form name
            return (match.group(1), int(match.group(2)), int(match.group(3)), int(match.group(4)), match.group(5))
        return None, None, None, None, None

    def process_xbrl_directory_and_push_database(self, db_type, username, password, server, database, xbrl_zip_directory,
                                                 sec_ticker_info_helper, extracted_directory='.',
                                                 remove_extracted_file_after_done=False):
        logger.Logger.log(logger.LogLevel.INFO, 'Processing xbrl zip directory %s and push to database' % xbrl_zip_directory)
        xbrl_zip_files = SecXbrlHelper.get_all_xbrl_zip_files_from_directory(xbrl_zip_directory)

        for xbrl_zip_file in xbrl_zip_files:
            self.q.put(xbrl_zip_file)

        # Start threads to download
        threads = []
        for i in range(SecXbrlProcessor.MAX_PROCESSING_THREADS):
            t = threading.Thread(
                    target=self.process_xbrl_zip_file_and_push_database,
                    args=(db_type,
                          username,
                          password,
                          server,
                          database,
                          sec_ticker_info_helper,
                          extracted_directory,
                          remove_extracted_file_after_done))
            threads.append(t)
            t.start()

        for i in range(len(threads)):
            wait_thread = threads[i]
            logger.Logger.log(logger.LogLevel.INFO, 'Wait for thread %s' % wait_thread.name)
            wait_thread.join()
            logger.Logger.log(logger.LogLevel.INFO, 'Thread %s done' % wait_thread.name)

    def process_xbrl_zip_file_and_push_database(self, db_type, username, password, server, database,
                                                sec_ticker_info_helper, extracted_directory='.',
                                                remove_extracted_file_after_done=False):
        count = 0
        while not self.q.empty():
            try:
                count += 1
                zip_file_path = self.q.get()

                logger.Logger.log(logger.LogLevel.INFO, '(%s) Processing xbrl zip file (%d) %s and push to database' % (
                                  threading.current_thread().name, count, zip_file_path))

                (directory, xbrl_zip_file_name) = StringHelper.extract_directory_and_file_name_from_path(zip_file_path)
                (ticker, cik, year, quarter, form_name) = SecXbrlProcessor.parse_xbrl_zip_file_name(xbrl_zip_file_name)
                if (ticker is None or cik is None or year is None or quarter is None or form_name is None):
                    logger.Logger.log(logger.LogLevel.WARN, 'Cannot extract information from zip file %s' % zip_file_path)
                    continue
                print (ticker, cik, year, quarter, form_name)
                results = self.process_xbrl_zip_file(zip_file_path=zip_file_path,
                                                     extracted_directory=extracted_directory,
                                                     remove_extracted_file_after_done=remove_extracted_file_after_done)
                if results is None:
                    logger.Logger.log(logger.LogLevel.WARN, 'Found no results from file %s' % zip_file_path)
                    continue

                table_name = '%s_metrics' % ticker.lower()
                sec_xbrl_database_helper = SecXbrlDatabaseHelper(dbtype=db_type,
                                                                 username=username,
                                                                 password=password,
                                                                 server=server,
                                                                 database=database,
                                                                 table_name=table_name)

                metrics = sec_xbrl_database_helper.convert_parse_results_to_metrics(parse_results=results)
                metadata = {}
                metadata['year'] = year
                metadata['quarter'] = quarter
                metadata['form'] = form_name
                for metric in metrics:
                    metric.metadata = json.dumps(metadata)

                sec_xbrl_database_helper.insert_company_metrics_table(values=metrics)
            finally:
                self.q.task_done()

    def process_xbrl_zip_file(self, zip_file_path, extracted_directory='.', remove_extracted_file_after_done=False):
        logger.Logger.log(logger.LogLevel.INFO, 'Processing xbrl zip file %s' % zip_file_path)

        extracted_file_path = self.extract_xbrl_zip_file(zip_file_path=zip_file_path,
                                   extracted_directory=extracted_directory)
        if extracted_file_path is None:
            return None

        results = self.parse_xbrl(xbrl_file=extracted_file_path)

        if remove_extracted_file_after_done:
            os.remove(extracted_file_path)

        return results

    def extract_context(self, root):
        # Gather all the context informaiton.
        # key = context id
        # value = [startdate, enddate]
        context = {}
        for child in root:
            try:
                if not isinstance(child.tag, basestring):
                    continue

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
                else:
                    logger.Logger.log(logger.LogLevel.WARN, 'Context %s doesnot have either startdate %s or enddate' % (startDate, endDate))
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, e)
            finally:
                pass
        return context

    def extract_unit(self, root):
        # Gather all the unit informaiton.
        # key = unit id
        # value = unit measure
        unit = {}
        for child in root:
            try:
                if not isinstance(child.tag, basestring):
                    continue

                if child.tag.find('unit') == -1:
                    continue

                if 'id' not in child.attrib:
                    continue

                unit_id = child.attrib['id']
                for grandchild in child:
                    if grandchild.tag.find('measure') == -1 and grandchild.tag.find('divide') == -1:
                        continue

                    #<unit id="u001">
                    #    <measure>xbrli:shares</measure>
                    #</unit>
                    if grandchild.tag.find('measure') != -1:
                        unit[unit_id] = grandchild.text
                    elif grandchild.tag.find('divide') != -1:
                        # Example:
                        #<unit id="u002">
                        #<divide>
                        #  <unitNumerator>
                        #    <measure>iso4217:USD</measure>
                        #  </unitNumerator>
                        #  <unitDenominator>
                        #    <measure>xbrli:shares</measure>
                        #  </unitDenominator>
                        #</divide>
                        #</unit>
                        numerator = None
                        denominator = None
                        for great_grandchild in grandchild:
                            great_grandchild_tag = great_grandchild.tag.lower()
                            if great_grandchild_tag.find('numerator') != -1:
                                for greatgreat_grandchild in great_grandchild:
                                    greatgreat_grandchild_tag = greatgreat_grandchild.tag.lower()
                                    if greatgreat_grandchild_tag.find('measure') != -1:
                                        numerator = greatgreat_grandchild.text
                                        break
                            elif great_grandchild_tag.find('denominator') != -1:
                                for greatgreat_grandchild in great_grandchild:
                                    if greatgreat_grandchild_tag.find('measure') != -1:
                                        denominator = greatgreat_grandchild.text
                                        break
                        if numerator is not None and denominator is not None:
                            unit[unit_id] = numerator + '/' + denominator

            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, e)
            finally:
                pass

        return unit

    def parse_xbrl(self, xbrl_file):
        logger.Logger.log(logger.LogLevel.INFO, 'Parsing xbrl file %s' % xbrl_file)

        results = {}

        try:
            tree = etree.parse(xbrl_file)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.INFO, e)
            return results

        root = tree.getroot()
        context = self.extract_context(root)
        unit = self.extract_unit(root)

        reverse_nsmap = {}
        for namespace in root.nsmap:
            reverse_nsmap[root.nsmap[namespace]] = namespace

        for child in root:
            try:
                full_tag = child.tag
                attrib = child.attrib
                text_value = child.text

                if ((text_value is None) or (full_tag is None) or (attrib is None) or
                    ('unitRef' not in attrib) or ('contextRef' not in attrib) or
                    (attrib['unitRef'] not in unit) or (attrib['contextRef'] not in context)):
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
                unit_ref = attrib['unitRef']
                # For ex: results['GrossProfit'] = [[1000, '2014-01-01', '2014-04-01', 'iso4217:USD', 'http://xbrl.us/us-gaap/2009-01-31']]
                results[tag].append([StringHelper.parse_value_string(text_value),
                                    context[context_ref][0],
                                    context[context_ref][1],
                                    unit[unit_ref],
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
                return None

            zip_file.extract(xbrl_file, extracted_directory)
            return '%s/%s' % (extracted_directory, xbrl_file)
