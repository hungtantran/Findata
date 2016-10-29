package fin_database

import (
    "log"
)

type TickerInfoDatabase struct {
    dbType string
    dbTableName string
    dbConnector *MySqlConnector
}

func NewTickerInfoDatabase(
        dbType string,
        dbTableName string,
        dbConnector *MySqlConnector) *TickerInfoDatabase {
    log.Println(dbType, dbTableName)
    var tickerInfoDatabase *TickerInfoDatabase = new(TickerInfoDatabase);
    tickerInfoDatabase.dbType = dbType;
    tickerInfoDatabase.dbConnector = dbConnector;
    tickerInfoDatabase.dbTableName = dbTableName;
    return tickerInfoDatabase;
}

func (tickerInfoDatabase *TickerInfoDatabase) GetAllTickerInfo() []TickerInfo {
    rows, err := tickerInfoDatabase.dbConnector.GetConnector().Query("SELECT * FROM " + tickerInfoDatabase.dbTableName);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var tickerInfo TickerInfo;
    var allTickerInfo []TickerInfo;
    for rows.Next() {
        err := rows.Scan(
                &tickerInfo.Id,
                &tickerInfo.Ticker,
                &tickerInfo.TickerType,
                &tickerInfo.Name,
                &tickerInfo.Location,
                &tickerInfo.Cik,
                &tickerInfo.IpoYear,
                &tickerInfo.Sector,
                &tickerInfo.Industry,
                &tickerInfo.Exchange,
                &tickerInfo.Sic,
                &tickerInfo.Naics,
                &tickerInfo.ClassShare,
                &tickerInfo.FundType,
                &tickerInfo.FundFamily,
                &tickerInfo.AssetClass,
                &tickerInfo.Active,
                &tickerInfo.MetaData);
        if err != nil {
            log.Println(err);
        }
        allTickerInfo = append(allTickerInfo, tickerInfo);
    }
    err = rows.Err()
    if err != nil {
        log.Println(err);
    }
    log.Println("Found", len(allTickerInfo), "ticker info");
    return allTickerInfo;
}

func (tickerInfoDatabase *TickerInfoDatabase) Close() {
    tickerInfoDatabase.dbConnector.Close();
}