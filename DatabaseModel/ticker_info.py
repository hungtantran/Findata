__author__ = 'hungtantran'


class TickerInfo(object):
    def __init__(self, cik, ticker, name, ipo_year, sector, industry, exchange, sic, naics):
        self.cik = cik
        self.ticker = ticker
        self.name = name
        self.ipo_year = ipo_year
        self.sector = sector
        self.industry = industry
        self.exchange = exchange
        self.sic = sic
        self.naics = naics

