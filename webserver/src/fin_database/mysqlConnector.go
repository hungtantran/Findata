package fin_database

import (
    "database/sql"
    _ "github.com/go-sql-driver/mysql"
    "log"
)

type MySqlConnector struct {
    dbUserName string
    dbPassword string
    dbServer string
    dbDatabase string
    db *sql.DB
}

func NewMySqlConnector(
        dbUserName string, 
        dbPassword string,
        dbServer string,
        dbDatabase string) *MySqlConnector {
    log.Println(dbUserName, dbPassword, dbServer, dbDatabase)
    var mySqlConnector *MySqlConnector = new(MySqlConnector);
    mySqlConnector.dbUserName = dbUserName;
    mySqlConnector.dbPassword = dbPassword;
    mySqlConnector.dbServer = dbServer;
    mySqlConnector.dbDatabase = dbDatabase;

    connectionString :=
        mySqlConnector.dbUserName + ":" +
        mySqlConnector.dbPassword + "@tcp(" + 
        mySqlConnector.dbServer + ":3306)/" +
        mySqlConnector.dbDatabase + "?parseTime=true";
    log.Println("Connect to mysql database use connection string " + connectionString);
    db, err := sql.Open("mysql", connectionString)
	if err != nil {
		log.Println(err)
	}
    mySqlConnector.db = db;
    return mySqlConnector;
}

func (mySqlConnector *MySqlConnector) GetConnector() *sql.DB {
    return mySqlConnector.db;
} 

func (mySqlConnector *MySqlConnector) Close() {
    mySqlConnector.db.Close();
}