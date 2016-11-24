package fin_database

import (
    "log"
)

type ExchangeIndexInfoDatabase struct {
    dbType string
    dbTableName string
    dbConnector *MySqlConnector
}

func NewExchangeIndexInfoDatabase(
        dbType string,
        dbTableName string,
        dbConnector *MySqlConnector) *ExchangeIndexInfoDatabase {
    log.Println(dbType, dbTableName)
    var exchangeIndexInfoDatabase *ExchangeIndexInfoDatabase = new(ExchangeIndexInfoDatabase);
    exchangeIndexInfoDatabase.dbType = dbType;
    exchangeIndexInfoDatabase.dbConnector = dbConnector;
    exchangeIndexInfoDatabase.dbTableName = dbTableName;
    return exchangeIndexInfoDatabase;
}

func (exchangeIndexInfoDatabase *ExchangeIndexInfoDatabase) GetAllExchangeIndexInfo() map[int64]ExchangeIndexInfo {
    rows, err := exchangeIndexInfoDatabase.dbConnector.GetConnector().Query("SELECT * FROM " + exchangeIndexInfoDatabase.dbTableName);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var exchangeIndexInfo ExchangeIndexInfo;
    allExchangeIndexInfo := make(map[int64]ExchangeIndexInfo);
    for rows.Next() {
        err := rows.Scan(
                &exchangeIndexInfo.Id,
                &exchangeIndexInfo.Index,
                &exchangeIndexInfo.IndexType,
                &exchangeIndexInfo.Name,
                &exchangeIndexInfo.Location,
                &exchangeIndexInfo.Sector,
                &exchangeIndexInfo.Industry,
                &exchangeIndexInfo.Metadata);
        if err != nil {
            log.Println(err)
        }
        allExchangeIndexInfo[exchangeIndexInfo.Id.Int64] = exchangeIndexInfo;
    }
    err = rows.Err()
    if err != nil {
        log.Println(err)
    }
    log.Println("Found", len(allExchangeIndexInfo), "exchange index info");
    return allExchangeIndexInfo;
}

func (exchangeIndexInfoDatabase *ExchangeIndexInfoDatabase) Close() {
    exchangeIndexInfoDatabase.dbConnector.Close();
}