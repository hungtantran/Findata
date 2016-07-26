__author__ = 'hungtantran'


class TickerInfo(object):
    def __init__(
            self,
            id = None,
            ticker = None,
            ticker_type = None,
            name = None,
            location = None,
            cik = None,
            ipo_year = None,
            sector = None,
            industry = None,
            exchange = None,
            sic = None,
            naics = None,
            class_share = None,
            fund_type = None,
            fund_family = None,
            asset_class = None,
            active = None,
            metadata = None):
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
        

