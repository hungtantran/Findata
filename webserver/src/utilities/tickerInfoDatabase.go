package main

import (
    "database/sql"
    _ "github.com/go-sql-driver/mysql"
    "log"
)

type TickerInfo struct {
    id sql.NullInt64
    ticker sql.NullString
    tickerType sql.NullString
    name sql.NullString
    location sql.NullString
    cik sql.NullString
    ipoYear sql.NullInt64
    sector sql.NullString
    industry sql.NullString
    exchange sql.NullString
    sic sql.NullInt64
    naics sql.NullInt64
    classShare sql.NullString
    fundType sql.NullString
    fundFamily sql.NullString
    assetClass sql.NullString
    active sql.NullInt64
    metaData sql.NullString
}

func (tickerInfo *TickerInfo) String() string {
    return  string(tickerInfo.id.Int64) + " " +
            tickerInfo.ticker.String + " " +
            tickerInfo.tickerType.String + " " +
            tickerInfo.name.String + " " +
            tickerInfo.location.String + " " +
            tickerInfo.cik.String + " " +
            string(tickerInfo.ipoYear.Int64) + " " +
            tickerInfo.sector.String + " " +
            tickerInfo.industry.String + " " +
            tickerInfo.exchange.String + " " +
            string(tickerInfo.sic.Int64) + " " +
            string(tickerInfo.naics.Int64) + " " +
            tickerInfo.classShare.String + " " +
            tickerInfo.fundType.String + " " +
            tickerInfo.fundFamily.String + " " +
            tickerInfo.assetClass.String + " " +
            string(tickerInfo.active.Int64) + " " +
            tickerInfo.metaData.String;
}

type TickerInfoDatabase struct {
    dbType string
    dbUserName string
    dbPassword string
    dbServer string
    dbDatabase string
    dbTableName string
    db *sql.DB
}

func NewTickerInfoDatabase(
        dbType string,
        dbUserName string, 
        dbPassword string,
        dbServer string,
        dbDatabase string,
        dbTableName string) *TickerInfoDatabase {
    log.Println(dbType, dbUserName, dbPassword, dbServer, dbDatabase, dbTableName)
    var tickerInfoDatabase *TickerInfoDatabase = new(TickerInfoDatabase);
    tickerInfoDatabase.dbType = dbType;
    tickerInfoDatabase.dbUserName = dbUserName;
    tickerInfoDatabase.dbPassword = dbPassword;
    tickerInfoDatabase.dbServer = dbServer;
    tickerInfoDatabase.dbDatabase = dbDatabase;
    tickerInfoDatabase.dbTableName = dbTableName;

    connectionString :=
        tickerInfoDatabase.dbUserName + ":" +
        tickerInfoDatabase.dbPassword + "@tcp(" + 
        tickerInfoDatabase.dbServer + ":3306)/" +
        tickerInfoDatabase.dbDatabase;
    log.Println("Connect to ticker info database use connection string " + connectionString);
    db, err := sql.Open(tickerInfoDatabase.dbType, connectionString)
	if err != nil {
		log.Println(err)
	}
    tickerInfoDatabase.db = db;
    return tickerInfoDatabase;
}

func (tickerInfoDatabase *TickerInfoDatabase) getAllTickerInfo() []TickerInfo {
    rows, err := tickerInfoDatabase.db.Query("SELECT * FROM ticker_info");
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var tickerInfo TickerInfo;
    var allTickerInfo []TickerInfo;
    for rows.Next() {
        err := rows.Scan(
                &tickerInfo.id,
                &tickerInfo.ticker,
                &tickerInfo.tickerType,
                &tickerInfo.name,
                &tickerInfo.location,
                &tickerInfo.cik,
                &tickerInfo.ipoYear,
                &tickerInfo.sector,
                &tickerInfo.industry,
                &tickerInfo.exchange,
                &tickerInfo.sic,
                &tickerInfo.naics,
                &tickerInfo.classShare,
                &tickerInfo.fundType,
                &tickerInfo.fundFamily,
                &tickerInfo.assetClass,
                &tickerInfo.active,
                &tickerInfo.metaData);
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

func (tickerInfoDatabase *TickerInfoDatabase) close() {
    tickerInfoDatabase.db.Close();
}