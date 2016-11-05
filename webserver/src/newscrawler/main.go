package main

import (
	"log"
    //"io/ioutil"
    "fin_database"
)

func main() {
	// Initialize logger to output filename
    log.SetFlags(log.Lshortfile);
    // Initialize configuration constants
    var config *ProdConfig;
    config.initializeConfig();

	var mysqlConnector *fin_database.MySqlConnector =  fin_database.NewMySqlConnector(
        mysqlUsername,
        mysqlPassword,
        mysqlServer,
        mysqlDatabase);

    var newsInfoDatabase *fin_database.NewsInfoDatabase = fin_database.NewNewsInfoDatabase(
        dbType,
        "news_info",
        mysqlConnector);

    var newsContentDatabase *fin_database.NewsContentDatabase = fin_database.NewNewsContentDatabase(
        dbType,
        "news_content",
        mysqlConnector);

	var nytimesCrawler *NYTimesCrawler = NewNYTimesCrawler(
        newsInfoDatabase,
        newsContentDatabase,
        /* startDayFromToday */ 415,
        /* endDayFromToday */ 2000,
        /* maxPageDepthPerDay */ 5,
        /* updateFrequencySecs */ 5 * 60 * 60,
        /* waitSecsBeforeRestart */ 20);
	nytimesCrawler.Crawl();
    
    /*json, err := ioutil.ReadFile("D:\\Users\\hungtantran\\PycharmProjects\\Models\\Rand\\NYTImes_response");
    if (err != nil) {
        log.Println(err);
        return;
    }
    content := string(json);
    log.Println(content);
    nytimesCrawler.ParseOnePage(json);*/ 
}