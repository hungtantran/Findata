package fin_database

import (
    "log"
)

type NewsContentDatabase struct {
    dbType string
    dbTableName string
    dbConnector *MySqlConnector
}

func NewNewsContentDatabase(
        dbType string,
        dbTableName string,
        dbConnector *MySqlConnector) *NewsContentDatabase {
    log.Println(dbType, dbTableName)
    var newsContentDatabase *NewsContentDatabase = new(NewsContentDatabase);
    newsContentDatabase.dbType = dbType;
    newsContentDatabase.dbConnector = dbConnector;
    newsContentDatabase.dbTableName = dbTableName;
    return newsContentDatabase;
}

func (newsContentDatabase *NewsContentDatabase) GetAllNewsContent() []NewsContent {
    rows, err := newsContentDatabase.dbConnector.GetConnector().Query("SELECT * FROM " + newsContentDatabase.dbTableName);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var newsContent NewsContent;
    var allNewsContent []NewsContent;
    for rows.Next() {
        err := rows.Scan(
                &newsContent.Id,
                &newsContent.FullData);
        if err != nil {
            log.Println(err);
        }
        allNewsContent = append(allNewsContent, newsContent);
    }
    err = rows.Err()
    if err != nil {
        log.Println(err);
    }
    log.Println("Found", len(allNewsContent), "news content");
    return allNewsContent;
}

func (newsContentDatabase *NewsContentDatabase) InsertNewsContent(newsContent *NewsContent) bool {
    stmt, err := newsContentDatabase.dbConnector.GetConnector().Prepare(
            "INSERT " + newsContentDatabase.dbTableName + " SET id=?, full_data=?");
    defer stmt.Close();
    if err != nil {
        log.Println(err);
        return false;
    }

    _, err = stmt.Exec(
            newsContent.Id,
            newsContent.FullData);
    if err != nil {
        log.Println(err);
        return false;
    }

    return true;
}

func (newsContentDatabase *NewsContentDatabase) Close() {
    newsContentDatabase.dbConnector.Close();
}