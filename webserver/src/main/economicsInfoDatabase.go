package main

import (
    "database/sql"
    "fmt"
    _ "github.com/go-sql-driver/mysql"
    "log"
)

// TODO: merge EconomicsInfo into DataSource type
type EconomicsInfo struct {
    id sql.NullInt64
    name sql.NullString
    location sql.NullString
    category sql.NullString
    typeStr sql.NullString
    source sql.NullString
    metadata sql.NullString   
}

func (economicsInfo *EconomicsInfo) String() string {
    return  string(economicsInfo.id.Int64) + " " +
            economicsInfo.name.String + " " +
            economicsInfo.location.String + " " +
            economicsInfo.category.String + " " +            
            economicsInfo.typeStr.String + " " +
            economicsInfo.source.String + " " +
            economicsInfo.metadata.String;
}

type EconomicsInfoDatabase struct {
    dbType string
    dbUserName string
    dbPassword string
    dbServer string
    dbDatabase string
    dbTableName string
    db *sql.DB
}

func NewEconomicsInfoDatabase(
        dbType string,
        dbUserName string, 
        dbPassword string,
        dbServer string,
        dbDatabase string,
        dbTableName string) *EconomicsInfoDatabase {
    fmt.Println(dbType, dbUserName, dbPassword, dbServer, dbDatabase, dbTableName)
    var economicsInfoDatabase *EconomicsInfoDatabase = new(EconomicsInfoDatabase);
    economicsInfoDatabase.dbType = dbType;
    economicsInfoDatabase.dbUserName = dbUserName;
    economicsInfoDatabase.dbPassword = dbPassword;
    economicsInfoDatabase.dbServer = dbServer;
    economicsInfoDatabase.dbDatabase = dbDatabase;
    economicsInfoDatabase.dbTableName = dbTableName;

    connectionString :=
        economicsInfoDatabase.dbUserName + ":" +
        economicsInfoDatabase.dbPassword + "@tcp(" + 
        economicsInfoDatabase.dbServer + ":3306)/" +
        economicsInfoDatabase.dbDatabase;
    fmt.Println("Connect to economics info database use connection string " + connectionString);
    db, err := sql.Open(economicsInfoDatabase.dbType, connectionString)
	if err != nil {
		log.Fatal(err)
	}
    economicsInfoDatabase.db = db;
    return economicsInfoDatabase;
}

func (economicsInfoDatabase *EconomicsInfoDatabase) getAllEconomicsInfo() []EconomicsInfo {
    rows, err := economicsInfoDatabase.db.Query("SELECT * FROM " + economicsInfoDatabase.dbTableName);
    if err != nil {
        log.Fatal(err)
    }
    defer rows.Close()
    var economicsInfo EconomicsInfo;
    var allEconomicsInfo []EconomicsInfo;
    for rows.Next() {
        err := rows.Scan(
                &economicsInfo.id,
                &economicsInfo.name,
                &economicsInfo.location,
                &economicsInfo.category,
                &economicsInfo.typeStr,
                &economicsInfo.source,
                &economicsInfo.metadata);
        if err != nil {
            log.Fatal(err)
        }
        allEconomicsInfo = append(allEconomicsInfo, economicsInfo);
    }
    err = rows.Err()
    if err != nil {
        log.Fatal(err)
    }
    log.Println("Found", len(allEconomicsInfo), "economics info");
    return allEconomicsInfo;
}

func (economicsInfoDatabase *EconomicsInfoDatabase) close() {
    economicsInfoDatabase.db.Close();
}