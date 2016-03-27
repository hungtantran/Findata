__author__ = 'hungtantran'


from generic_parser import GenericParser
from string_helper import StringHelper

class CsvParser(GenericParser):
    def __init__(self):
        pass

    def parse(self, source_name, max_num_results=0):
        dates = []
        titles = []
        results = []
        with open(source_name) as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            if len(lines) == 0:
                return results

            # The first line should be a title in the form like (Date, Dows, SP500)
            header_titles = lines[0].split(',')
            if len(header_titles) <= 1:
                return results

            # The first title must be Date
            if header_titles[0] != 'Date':
                return results

            # Populate the titles list
            for i in range(1, len(header_titles)):
                titles.append(header_titles[i])
                results.append([])

            num_results = 0
            for i in range(1, len(lines)):
                values = lines[i].split(',')
                if len(values) != len(header_titles):
                    continue

                if (max_num_results > 0) and (num_results >= max_num_results):
                    break
                else:
                    num_results += 1

                # Append date to the new line
                dates.append(values[0])

                # Append new values to the results
                for j in range(1, len(values)):
                    results[j - 1].append(StringHelper.parse_value_string(values[j]))

        return (titles, dates, results)

