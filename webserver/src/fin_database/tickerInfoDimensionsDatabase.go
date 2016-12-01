package fin_database

import (
    "log"
)

type TickerInfoDimensionsDatabase struct {
    dbType string
    dbTableName string
    dbConnector *MySqlConnector
}

func NewTickerInfoDimensionsDatabase(
        dbType string,
        dbTableName string,
        dbConnector *MySqlConnector) *TickerInfoDimensionsDatabase {
    log.Println(dbType, dbTableName)
    var tickerInfoDimensionsDatabase *TickerInfoDimensionsDatabase = new(TickerInfoDimensionsDatabase);
    tickerInfoDimensionsDatabase.dbType = dbType;
    tickerInfoDimensionsDatabase.dbConnector = dbConnector;
    tickerInfoDimensionsDatabase.dbTableName = dbTableName;
    return tickerInfoDimensionsDatabase;
}

func (tickerInfoDimensionsDatabase *TickerInfoDimensionsDatabase) GetAllTickerInfoDimensions() map[string]TickerInfoDimension {
    rows, err := tickerInfoDimensionsDatabase.dbConnector.GetConnector().Query("SELECT * FROM " + tickerInfoDimensionsDatabase.dbTableName);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var tickerInfoDimension TickerInfoDimension;
    allTickerInfoDimensions := make(map[string]TickerInfoDimension);
    for rows.Next() {
        err := rows.Scan(
                &tickerInfoDimension.Id,
                &tickerInfoDimension.Abbrv,
                &tickerInfoDimension.Name,
                &tickerInfoDimension.NameHash,
                &tickerInfoDimension.Unit,
                &tickerInfoDimension.Metadata);
        if err != nil {
            log.Println(err);
        }
        allTickerInfoDimensions[tickerInfoDimension.Abbrv.String] = tickerInfoDimension;
    }
    err = rows.Err()
    if err != nil {
        log.Println(err);
    }
    log.Println("Found", len(allTickerInfoDimensions), "ticker info dimensions");
    return allTickerInfoDimensions;
}

func (tickerInfoDimensionsDatabase *TickerInfoDimensionsDatabase) Close() {
    tickerInfoDimensionsDatabase.dbConnector.Close();
}