package fin_database

import (
    "fmt"
    "log"
    "time"
)

type NewsInfoDatabase struct {
    dbType string
    dbTableName string
    dbConnector *MySqlConnector
}

func NewNewsInfoDatabase(
        dbType string,
        dbTableName string,
        dbConnector *MySqlConnector) *NewsInfoDatabase {
    log.Println(dbType, dbTableName)
    var newsInfoDatabase *NewsInfoDatabase = new(NewsInfoDatabase);
    newsInfoDatabase.dbType = dbType;
    newsInfoDatabase.dbConnector = dbConnector;
    newsInfoDatabase.dbTableName = dbTableName;
    return newsInfoDatabase;
}

func (newsInfoDatabase *NewsInfoDatabase) GetLatestDate() time.Time {
    rows, err := newsInfoDatabase.dbConnector.GetConnector().Query("SELECT date FROM " + newsInfoDatabase.dbTableName + " ORDER BY date DESC LIMIT 1");
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var latestTime time.Time;
    for rows.Next() {
        err := rows.Scan(&latestTime);
        if err != nil {
            log.Println(err);
        }
    }
    err = rows.Err()
    if err != nil {
        log.Println(err);
    }
    return latestTime;
}

func (newsInfoDatabase *NewsInfoDatabase) GetAllNewsInfo() []NewsInfo {
    rows, err := newsInfoDatabase.dbConnector.GetConnector().Query("SELECT * FROM " + newsInfoDatabase.dbTableName);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var newsInfo NewsInfo;
    var allNewsInfo []NewsInfo;
    for rows.Next() {
        err := rows.Scan(
                &newsInfo.Id,
                &newsInfo.Source,
                &newsInfo.Date,
                &newsInfo.Headline,
                &newsInfo.PrintHeadline,
                &newsInfo.Abstract,
                &newsInfo.Section,
                &newsInfo.Subsection,
                &newsInfo.Tags,
                &newsInfo.Keywords,
                &newsInfo.Link,
                &newsInfo.Authors,
                &newsInfo.Metadata);
        if err != nil {
            log.Println(err);
        }
        allNewsInfo = append(allNewsInfo, newsInfo);
    }
    err = rows.Err()
    if err != nil {
        log.Println(err);
    }
    log.Println("Found", len(allNewsInfo), "news info");
    return allNewsInfo;
}

func (newsInfoDatabase *NewsInfoDatabase) GetNewsInfo(startId int, numResults int) []NewsInfo {
    query := fmt.Sprintf("SELECT * FROM %s ORDER BY id LIMIT %d,%d", newsInfoDatabase.dbTableName, startId, numResults);
    rows, err := newsInfoDatabase.dbConnector.GetConnector().Query(query);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var newsInfo NewsInfo;
    var allNewsInfo []NewsInfo;
    for rows.Next() {
        err := rows.Scan(
                &newsInfo.Id,
                &newsInfo.Source,
                &newsInfo.Date,
                &newsInfo.Headline,
                &newsInfo.PrintHeadline,
                &newsInfo.Abstract,
                &newsInfo.Section,
                &newsInfo.Subsection,
                &newsInfo.Tags,
                &newsInfo.Keywords,
                &newsInfo.Link,
                &newsInfo.Authors,
                &newsInfo.Metadata);
        if err != nil {
            log.Println(err);
        }
        allNewsInfo = append(allNewsInfo, newsInfo);
    }
    err = rows.Err()
    if err != nil {
        log.Println(err);
    }
    log.Println("Found", len(allNewsInfo), "news info");
    return allNewsInfo;
}

func (newsInfoDatabase *NewsInfoDatabase) InsertNewsInfo(newsInfo *NewsInfo) int64 {
    stmt, err := newsInfoDatabase.dbConnector.GetConnector().Prepare(
            "INSERT " + newsInfoDatabase.dbTableName + " SET id=?, source=?, date=?, headline=?, print_headline=?, abstract=?, section=?, subsection=?, tags=?, keywords=?, link=?, authors=?, metadata=?");
    if err != nil {
        log.Println(err);
        return -1;
    }

    res, err := stmt.Exec(
            newsInfo.Id,
            newsInfo.Source,
            newsInfo.Date,
            newsInfo.Headline,
            newsInfo.PrintHeadline,
            newsInfo.Abstract,
            newsInfo.Section,
            newsInfo.Subsection,
            newsInfo.Tags,
            newsInfo.Keywords,
            newsInfo.Link,
            newsInfo.Authors,
            newsInfo.Metadata);
    if err != nil {
        log.Println(err);
        return -1;
    }

    lastId, err := res.LastInsertId();
    if err != nil {
        log.Println(err);
        return -1;
    }

    stmt.Close();

    return lastId;
}

func (newsInfoDatabase *NewsInfoDatabase) Close() {
    newsInfoDatabase.dbConnector.Close();
}