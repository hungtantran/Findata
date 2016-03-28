__author__ = 'hungtantran'


from yahoo_historical_parser import YahooHistoricalParser
from parser_to_file import ParserToFile


def main():
    links = {}

    for link in links:
        parser = YahooHistoricalParser(sleep_secs = 3)
        (titles, dates, results) = parser.parse(source_name=link)
        ParserToFile.write_parse_result_to_file(titles, dates, results,
                                                output_file_name=links[link],
                                                delimiter='\t')


if __name__ == '__main__':
    main()