__author__ = 'hungtantran'


class TickerInfo(object):
    def __init__(self, id, ticker, ticker_type, name, location, cik, ipo_year, sector, industry, exchange, sic, naics, class_share, fund_type, fund_family, asset_class, active, metadata):
        self.id = id
        self.ticker = ticker
        self.ticker_type = ticker_type
        self.name = name
        self.location = location
        self.cik = cik
        self.ipo_year = ipo_year
        self.sector = sector
        self.industry = industry
        self.exchange = exchange
        self.sic = sic
        self.naics = naics
        self.class_share = class_share
        self.fund_type = fund_type
        self.fund_family = fund_family
        self.asset_class = asset_class
        self.active = active
        self.metadata = metadata
        

