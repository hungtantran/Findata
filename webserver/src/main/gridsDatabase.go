package main

import (
    "database/sql"
    "fmt"
    _ "github.com/go-sql-driver/mysql"
    "log"
)

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

type GridsDatabase struct {
    dbType string
    dbUserName string
    dbPassword string
    dbServer string
    dbDatabase string
    dbTableName string
    db *sql.DB
}

func NewGridsDatabase(
        dbType string,
        dbUserName string, 
        dbPassword string,
        dbServer string,
        dbDatabase string,
        dbTableName string) *GridsDatabase {
    log.Println(dbType, dbUserName, dbPassword, dbServer, dbDatabase, dbTableName)
    var gridsDatabase *GridsDatabase = new(GridsDatabase);
    gridsDatabase.dbType = dbType;
    gridsDatabase.dbUserName = dbUserName;
    gridsDatabase.dbPassword = dbPassword;
    gridsDatabase.dbServer = dbServer;
    gridsDatabase.dbDatabase = dbDatabase;
    gridsDatabase.dbTableName = dbTableName;

    connectionString :=
        gridsDatabase.dbUserName + ":" +
        gridsDatabase.dbPassword + "@tcp(" + 
        gridsDatabase.dbServer + ":3306)/" +
        gridsDatabase.dbDatabase;
    log.Println("Connect to grids database use connection string " + connectionString);
    db, err := sql.Open(gridsDatabase.dbType, connectionString)
	if err != nil {
		log.Println(err)
	}
    gridsDatabase.db = db;
    return gridsDatabase;
}

func (gridsDatabase *GridsDatabase) GetGrid(userid int64) *Grid {
    rows, err := gridsDatabase.db.Query("SELECT * FROM grids WHERE userid = ? LIMIT 1", userid);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var grid *Grid;
    grid = nil;
    if rows.Next() {
        grid = new(Grid);
        err := rows.Scan(
                &grid.Id,
                &grid.Name,
                &grid.Userid,
                &grid.Grid);
        if err != nil {
            log.Println(err);
        }
    }
    return grid;
}

func (gridsDatabase *GridsDatabase) InsertGrid(name string, userid int64, grid string) bool {
    stmt, err := gridsDatabase.db.Prepare("INSERT grids SET name=?, userid=?, grid=?");
    if err != nil {
        log.Println(err);
        return false;
    }

    res, err := stmt.Exec(name, userid, grid);
    if err != nil {
        log.Println(err);
        return false;
    }

    id, err := res.LastInsertId();
    if err != nil {
        log.Println(err);
        return false;
    }

    log.Println(id);
    return true;
}

func (gridsDatabase *GridsDatabase) close() {
    gridsDatabase.db.Close();
}