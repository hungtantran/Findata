package utilities

type TickerInfoElastic struct {
    Id int64 `json:"id"`
    Ticker string `json:"ticker"`
    Ticker_type string `json:"ticker_type"`
    Name string `json:"name"`
    Location string `json:"location"`
    Cik string `json:"cik"`
    Ipo_year int64 `json:"ipo_year"`
    Sector string `json:"sector"`
    Industry string `json:"industry"`
    Exchange string `json:"exchange"`
    Sic int64 `json:"sic"`
    Naics int64 `json:"naics"`
    Class_share string `json:"class_share"`
    Fund_type string `json:"fund_type"`
    Fund_family string `json:"fund_family"`
    Asset_class string `json:"asset_class"`
    Active int64 `json:"active"`
    Metadata string `json:"metadata"`
}

type ExchangeIndexInfoElastic struct {
    Id int64 `json:"id"`
    Index string `json:"index"`
    IndexType string `json:"index_type"`
    Name string `json:"name"`
    Location string `json:"location"`
    Sector string `json:"sector"`
    Industry string `json:"industry"`
    Metadata string `json:"metadata"`
}

type EconomicsInfoElastic struct {
    Id int64 `json:"id"`
    Name string `json:"name"`
    Location string `json:"location"`
    Category string `json:"category"`
    TypeStr string `json:"type"`
    Source string `json:"source"`
    Metadata string `json:"metadata"`
}

type NewsInfoElastic struct {
    Id int64 `json:"id"`
    Source string `json:"source"`
    Date string `json:"date"`
    Headline string `json:"headline"`
    PrintHeadline string `json:"print_headline"`
    Abstract string `json:"abstract"`
    Section string `json:"section"`
    Subsection string `json:"subsection"`
    Tags string `json:"tags"`
    Keywords string `json:"keywords"`
    Link string `json:"link"`
    Authors string `json:"authors"`
    Metadata string `json:"metadata"`
}
