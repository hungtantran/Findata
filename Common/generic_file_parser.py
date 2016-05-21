__author__ = 'hungtantran'


from generic_parser import GenericParser
from string_helper import StringHelper

class GenericFileParser(GenericParser):
    def __init__(self):
        pass

    def parse_content(self, content, delimiter='\t', has_title=True, max_num_results=0):
        titles = []
        results = []

        lines = content.split('\n')
        lines = [line.strip() for line in lines]
        if len(lines) == 0:
            return (titles, results)

        if has_title:
            header_titles = lines[0].split(delimiter)
            if len(header_titles) <= 1:
                return (titles, results)

        # Populate the titles list
        for i in range(len(header_titles)):
            titles.append(header_titles[i])
            results.append([])

        num_results = 0
        for i in range(1, len(lines)):
            values = lines[i].split(delimiter)
            if len(values) != len(header_titles):
                continue

            if (max_num_results > 0) and (num_results >= max_num_results):
                break
            else:
                num_results += 1

            # Append new values to the results
            for j in range(len(values)):
                results[j].append(values[j])

        return (titles, results)

    def parse(self, source_name, delimiter='\t', has_title=True, max_num_results=0):
        with open(source_name) as f:
            return self.parse_content(content=f.read(),
                                      delimiter=delimiter,
                                      has_title=has_title,
                                      max_num_results=max_num_results)

