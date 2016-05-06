__author__ = 'hungtantran'


class FundInfo(object):
    def __init__(self, id, ticker, name, family, class_share, fund_type, metadata):
        self.id = id
        self.ticker = ticker
        self.name = name
        self.family = family
        self.class_share = class_share
        self.fund_type = fund_type
        self.metadata = metadata