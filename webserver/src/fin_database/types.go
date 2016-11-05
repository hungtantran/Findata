package fin_database

import (
    "database/sql"
    "fmt"
    "strconv"
    "time"
)

// Data type
type TickerInfo struct {
    Id sql.NullInt64 `json:"id"`
    Ticker sql.NullString `json:"ticker"`
    TickerType sql.NullString `json:"ticker_type"`
    Name sql.NullString `json:"name"`
    Location sql.NullString `json:"location"`
    Cik sql.NullString `json:"cik"`
    IpoYear sql.NullInt64 `json:"ipo_year"`
    Sector sql.NullString `json:"sector"`
    Industry sql.NullString `json:"industry"`
    Exchange sql.NullString `json:"exchange"`
    Sic sql.NullInt64 `json:"sic"`
    Naics sql.NullInt64 `json:"naics"`
    ClassShare sql.NullString `json:"class_share"`
    FundType sql.NullString `json:"fund_type"`
    FundFamily sql.NullString `json:"fund_family"`
    AssetClass sql.NullString `json:"asset_class"`
    Active sql.NullInt64 `json:"active"`
    MetaData sql.NullString `json:"metadata"`
}

func (tickerInfo *TickerInfo) String() string {
    return  string(tickerInfo.Id.Int64) + " " +
            tickerInfo.Ticker.String + " " +
            tickerInfo.TickerType.String + " " +
            tickerInfo.Name.String + " " +
            tickerInfo.Location.String + " " +
            tickerInfo.Cik.String + " " +
            string(tickerInfo.IpoYear.Int64) + " " +
            tickerInfo.Sector.String + " " +
            tickerInfo.Industry.String + " " +
            tickerInfo.Exchange.String + " " +
            string(tickerInfo.Sic.Int64) + " " +
            string(tickerInfo.Naics.Int64) + " " +
            tickerInfo.ClassShare.String + " " +
            tickerInfo.FundType.String + " " +
            tickerInfo.FundFamily.String + " " +
            tickerInfo.AssetClass.String + " " +
            string(tickerInfo.Active.Int64) + " " +
            tickerInfo.MetaData.String;
}

type Metric struct {
    Id sql.NullInt64
    MetricName sql.NullString
    Value sql.NullFloat64
    Unit sql.NullString
    StartDate time.Time
    EndDate time.Time
    MetaData sql.NullString
}

func (metric *Metric) String() string {
    return  string(metric.Id.Int64) + " " +
            metric.MetricName.String + " " +
            strconv.FormatFloat(metric.Value.Float64, 'f', 6, 64) + " " +
            metric.Unit.String + " " +
            time.Time.String(metric.StartDate) + " " +
            time.Time.String(metric.EndDate) + " " +
            metric.MetaData.String;
}

type ResultMetric struct {
    V float64
    T time.Time
}

type User struct {
    Id sql.NullInt64
    TypeStr sql.NullString
    Username sql.NullString
    Fullname sql.NullString
    Email sql.NullString
    Passwordhash sql.NullString
    Passwordsalt sql.NullString
    Metadata sql.NullString
    Isdisabled sql.NullBool
}

func (user *User) String() string {
    return fmt.Sprintf("%d %s %s %s %s %s %s %s %t",
		user.Id.Int64,
        user.TypeStr.String,
        user.Username.String,
        user.Fullname.String,
        user.Email.String,
        user.Passwordhash.String,
        user.Passwordsalt.String,
        user.Metadata.String,
        user.Isdisabled.Bool);
}

type ExchangeIndexInfo struct {
    Id sql.NullInt64 `json:"id"`
    Index sql.NullString `json:"index"`
    IndexType sql.NullString `json:"index_type"`
    Name sql.NullString `json:"name"`
    Location sql.NullString `json:"location"`
    Sector sql.NullString `json:"sector"`
    Industry sql.NullString `json:"industry"`
    Metadata sql.NullString `json:"metadata"`
}

func (exchangeIndexInfo *ExchangeIndexInfo) String() string {
    return  string(exchangeIndexInfo.Id.Int64) + " " +
            exchangeIndexInfo.Index.String + " " +
            exchangeIndexInfo.IndexType.String + " " +
            exchangeIndexInfo.Name.String + " " +            
            exchangeIndexInfo.Location.String + " " +
            exchangeIndexInfo.Sector.String + " " +
            exchangeIndexInfo.Industry.String + " " +
            exchangeIndexInfo.Metadata.String;
}

type EconomicsInfo struct {
    Id sql.NullInt64 `json:"id"`
    Name sql.NullString `json:"name"`
    Location sql.NullString `json:"location"`
    Category sql.NullString `json:"category"`
    TypeStr sql.NullString `json:"type"`
    Source sql.NullString `json:"source"`
    Metadata sql.NullString `json:"metadata"` 
}

func (economicsInfo *EconomicsInfo) String() string {
    return  string(economicsInfo.Id.Int64) + " " +
            economicsInfo.Name.String + " " +
            economicsInfo.Location.String + " " +
            economicsInfo.Category.String + " " +            
            economicsInfo.TypeStr.String + " " +
            economicsInfo.Source.String + " " +
            economicsInfo.Metadata.String;
}

type Grid struct {
    Id sql.NullInt64
    Name sql.NullString
    Userid sql.NullInt64
    Grid sql.NullString
}

func (grid *Grid) String() string {
    return fmt.Sprintf("%d %s %d %s",
		grid.Id.Int64,
        grid.Name.String,
        grid.Userid.Int64,
        grid.Grid.String);
}

type NewsInfo struct {
    Id sql.NullInt64
    Source sql.NullString
    Date time.Time
    Headline sql.NullString
    PrintHeadline sql.NullString
    Abstract sql.NullString
    Section sql.NullString
    Subsection sql.NullString
    Tags sql.NullString
    Keywords sql.NullString
    Link sql.NullString
    Authors sql.NullString
    Metadata sql.NullString
}

type NewsContent struct {
    Id sql.NullInt64
    FullData sql.NullString
}