package fin_database

import (
    "strings"
    "strconv"
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

func (tickerInfoDatabase *TickerInfoDatabase) GetAllTickerInfo() map[int64]TickerInfo {
    allTickerInfo := make(map[int64]TickerInfo);
    
	rows, err := tickerInfoDatabase.dbConnector.GetConnector().Query("SHOW TABLES LIKE 'ticker_info_%_metrics'");
    if err != nil {
        return allTickerInfo;
    }
    defer rows.Close()
    existingTickerInfoIds := make(map[int64]int);
    for rows.Next() {
		var tickerInfoTableName string;
        rows.Scan(&tickerInfoTableName);
		nameParts := strings.Split(tickerInfoTableName, "_");
		if (len(nameParts) != 4) {
			continue;
		}
		id, _ := strconv.ParseInt(nameParts[2], 10, 64);
		existingTickerInfoIds[id] = 1;
    }

    rows, err = tickerInfoDatabase.dbConnector.GetConnector().Query("SELECT * FROM " + tickerInfoDatabase.dbTableName);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var tickerInfo TickerInfo;
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
        if _, ok := existingTickerInfoIds[tickerInfo.Id.Int64]; !ok {
			continue;
		}
        allTickerInfo[tickerInfo.Id.Int64] = tickerInfo;
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