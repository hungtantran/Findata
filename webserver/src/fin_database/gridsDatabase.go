package fin_database

import (
    "log"
)

type GridsDatabase struct {
    dbType string
    dbTableName string
    dbConnector *MySqlConnector
}

func NewGridsDatabase(
        dbType string,
        dbTableName string,
        dbConnector *MySqlConnector) *GridsDatabase {
    log.Println(dbType, dbTableName)
    var gridsDatabase *GridsDatabase = new(GridsDatabase);
    gridsDatabase.dbType = dbType;
    gridsDatabase.dbConnector = dbConnector;
    gridsDatabase.dbTableName = dbTableName;
    return gridsDatabase;
}

func (gridsDatabase *GridsDatabase) GetGrid(userid int64) *Grid {
    rows, err := gridsDatabase.dbConnector.GetConnector().Query("SELECT * FROM " + gridsDatabase.dbTableName + " WHERE userid = ? LIMIT 1", userid);
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
    stmt, err := gridsDatabase.dbConnector.GetConnector().Prepare(
            "INSERT " + gridsDatabase.dbTableName + " SET name=?, userid=?, grid=? ON DUPLICATE KEY UPDATE grid=?");
    if err != nil {
        log.Println(err);
        return false;
    }

    res, err := stmt.Exec(name, userid, grid, grid);
    if err != nil {
        log.Println(err);
        return false;
    }

    _, err = res.LastInsertId();
    if err != nil {
        log.Println(err);
        return false;
    }

    return true;
}

func (gridsDatabase *GridsDatabase) Close() {
    gridsDatabase.dbConnector.Close();
}