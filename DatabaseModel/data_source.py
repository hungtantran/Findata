__author__ = 'hungtantran'


class DataSource(object):
    def __init__(self, name, abbrv, type, subtype, city, country, region, tablename, source, frequency, tabletype,
                 link, description):
        self.name = name
        self.abbrv = abbrv
        self.type = type
        self.subtype = subtype
        self.city = city
        self.country = country
        self.region = region
        self.tablename = tablename
        self.source = source
        self.frequency = frequency
        self.tabletype = tabletype
        self.link = link
        self.description = description


class DataSourceType(object):
    def __init__(self, id, type, subtype):
        self.id = id
        self.type = type
        self.subtype = subtype

