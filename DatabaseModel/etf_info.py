__author__ = 'hungtantran'


class ETFInfo(object):
    def __init__(self, id, ticker, name, asset_class, sector, location, metadata):
        self.id = id
        self.ticker = ticker
        self.name = name
        self.asset_class = asset_class
        self.sector = sector
        self.location = location
        self.metadata = metadata