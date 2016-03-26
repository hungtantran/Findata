__author__ = 'hungtantran'


from file_parser import FileParser


class CsvParser(FileParser):
    def __init__(self):
        pass

    @staticmethod
    def parse_value_string(value_string):
        try:
            return float(value_string)
        except ValueError:
            return None

    def parse(self, file_name):
        dates = []
        titles = []
        results = []
        with open(file_name) as f:
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

            for i in range(1, len(lines)):
                values = lines[i].split(',')
                if len(values) != len(header_titles):
                    continue

                # Append date to the new line
                dates.append(values[0])

                # Append new values to the results
                for j in range(1, len(values)):
                    results[j - 1].append(CsvParser.parse_value_string(values[j]))

        return (titles, dates, results)

