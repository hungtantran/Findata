__author__ = 'hungtantran'


from yahoo_historical_parser import YahooHistoricalParser
from parser_to_file import ParserToFile


def main():
    links = {}
    links['http://finance.yahoo.com/q/hp?s=%5EGSPC&d=2&e=27&f=2016&g=d&a=0&b=3&c=1950&z=66&y=66'] = 'Yahoo_Data\sp500.txt'
    links['http://finance.yahoo.com/q/hp?s=%5EDJI&d=2&e=27&f=2016&g=d&a=0&b=29&c=1985&z=66&y=66'] = 'Yahoo_Data\dowjones.txt'

    for link in links:
        parser = YahooHistoricalParser(sleep_secs = 60)
        (titles, dates, results) = parser.parse(source_name=link)
        ParserToFile.write_parse_result_to_file(titles, dates, results,
                                                output_file_name=links[link],
                                                delimiter='\t')


if __name__ == '__main__':
    main()