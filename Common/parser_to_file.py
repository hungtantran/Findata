__author__ = 'hungtantran'


import logger

class ParserToFile(object):
    @staticmethod
    def write_parse_result_to_file(titles, dates, results, output_file_name, delimiter=','):
        if len(titles) != len(results):
            logger.Logger.log(logger.LogLevel.WARN, 'Number of titles %d does not match number of results array %d' %
                              (len(titles), len(results)))
            return

        for result in results:
            if len(dates) != len(result):
                logger.Logger.log(logger.LogLevel.WARN, 'Number of dates %d does not match number of result array %d' %
                                  (len(titles), len(result)))
                return
        try:
            f = open(output_file_name, 'w')

            # Write the first header line
            headers_arr = ['Date']
            for title in titles:
                headers_arr.append(title)
            headers_string = delimiter.join(headers_arr)
            headers_string += '\n'
            f.write(headers_string)

            # Write each row for each date
            for i in range(len(dates)):
                values_arr = [dates[i]]

                for j in range(len(results)):
                    values_arr.append(str(results[j][i]))

                values_string = delimiter.join(values_arr)
                values_string += '\n'
                f.write(values_string)

        finally:
            f.flush()
            f.close()