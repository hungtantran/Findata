package main

import (
    "database/sql"
    _ "github.com/go-sql-driver/mysql"
    "log"
)

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

type ExchangeIndexInfoDatabase struct {
    dbType string
    dbUserName string
    dbPassword string
    dbServer string
    dbDatabase string
    dbTableName string
    db *sql.DB
}

func NewExchangeIndexInfoDatabase(
        dbType string,
        dbUserName string, 
        dbPassword string,
        dbServer string,
        dbDatabase string,
        dbTableName string) *ExchangeIndexInfoDatabase {
    log.Println(dbType, dbUserName, dbPassword, dbServer, dbDatabase, dbTableName)
    var exchangeIndexInfoDatabase *ExchangeIndexInfoDatabase = new(ExchangeIndexInfoDatabase);
    exchangeIndexInfoDatabase.dbType = dbType;
    exchangeIndexInfoDatabase.dbUserName = dbUserName;
    exchangeIndexInfoDatabase.dbPassword = dbPassword;
    exchangeIndexInfoDatabase.dbServer = dbServer;
    exchangeIndexInfoDatabase.dbDatabase = dbDatabase;
    exchangeIndexInfoDatabase.dbTableName = dbTableName;

    connectionString :=
        exchangeIndexInfoDatabase.dbUserName + ":" +
        exchangeIndexInfoDatabase.dbPassword + "@tcp(" + 
        exchangeIndexInfoDatabase.dbServer + ":3306)/" +
        exchangeIndexInfoDatabase.dbDatabase;
    log.Println("Connect to exchange index info database use connection string " + connectionString);
    db, err := sql.Open(exchangeIndexInfoDatabase.dbType, connectionString)
	if err != nil {
		log.Println(err)
	}
    exchangeIndexInfoDatabase.db = db;
    return exchangeIndexInfoDatabase;
}

func (exchangeIndexInfoDatabase *ExchangeIndexInfoDatabase) getAllExchangeIndexInfo() []ExchangeIndexInfo {
    rows, err := exchangeIndexInfoDatabase.db.Query("SELECT * FROM exchange_index_info");
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var exchangeIndexInfo ExchangeIndexInfo;
    var allExchangeIndexInfo []ExchangeIndexInfo;
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
        allExchangeIndexInfo = append(allExchangeIndexInfo, exchangeIndexInfo);
    }
    err = rows.Err()
    if err != nil {
        log.Println(err)
    }
    log.Println("Found", len(allExchangeIndexInfo), "exchange index info");
    return allExchangeIndexInfo;
}

func (exchangeIndexInfoDatabase *ExchangeIndexInfoDatabase) close() {
    exchangeIndexInfoDatabase.db.Close();
}