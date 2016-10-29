package fin_database

import (
    "database/sql"
    "fmt"
    "strconv"
    "time"
)

// Data type
type TickerInfo struct {
    Id sql.NullInt64
    Ticker sql.NullString
    TickerType sql.NullString
    Name sql.NullString
    Location sql.NullString
    Cik sql.NullString
    IpoYear sql.NullInt64
    Sector sql.NullString
    Industry sql.NullString
    Exchange sql.NullString
    Sic sql.NullInt64
    Naics sql.NullInt64
    ClassShare sql.NullString
    FundType sql.NullString
    FundFamily sql.NullString
    AssetClass sql.NullString
    Active sql.NullInt64
    MetaData sql.NullString
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
    Id sql.NullInt64
    Index sql.NullString
    IndexType sql.NullString
    Name sql.NullString
    Location sql.NullString
    Sector sql.NullString
    Industry sql.NullString
    Metadata sql.NullString
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
    Id sql.NullInt64
    Name sql.NullString
    Location sql.NullString
    Category sql.NullString
    TypeStr sql.NullString
    Source sql.NullString
    Metadata sql.NullString   
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