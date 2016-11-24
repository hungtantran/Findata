package fin_database

import (
    "log"
)

type EconomicsInfoDatabase struct {
    dbType string
    dbTableName string
    dbConnector *MySqlConnector
}

func NewEconomicsInfoDatabase(
        dbType string,
        dbTableName string,
        dbConnector *MySqlConnector) *EconomicsInfoDatabase {
    log.Println(dbType, dbTableName)
    var economicsInfoDatabase *EconomicsInfoDatabase = new(EconomicsInfoDatabase);
    economicsInfoDatabase.dbType = dbType;
    economicsInfoDatabase.dbConnector = dbConnector;
    economicsInfoDatabase.dbTableName = dbTableName;
    return economicsInfoDatabase;
}

func (economicsInfoDatabase *EconomicsInfoDatabase) GetAllEconomicsInfo() map[int64]EconomicsInfo {
    rows, err := economicsInfoDatabase.dbConnector.GetConnector().Query("SELECT * FROM " + economicsInfoDatabase.dbTableName);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var economicsInfo EconomicsInfo;
    allEconomicsInfo := make(map[int64]EconomicsInfo);
    for rows.Next() {
        err := rows.Scan(
                &economicsInfo.Id,
                &economicsInfo.Name,
                &economicsInfo.Location,
                &economicsInfo.Category,
                &economicsInfo.TypeStr,
                &economicsInfo.Source,
                &economicsInfo.Metadata);
        if err != nil {
            log.Println(err)
        }
        allEconomicsInfo[economicsInfo.Id.Int64] = economicsInfo;
    }
    err = rows.Err()
    if err != nil {
        log.Println(err)
    }
    log.Println("Found", len(allEconomicsInfo), "economics info");
    return allEconomicsInfo;
}

func (economicsInfoDatabase *EconomicsInfoDatabase) Close() {
    economicsInfoDatabase.dbConnector.Close();
}