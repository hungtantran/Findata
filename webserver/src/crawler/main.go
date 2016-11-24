package main

import (
	"log"
    //"io/ioutil"
    "sync"

    "fin_database"
    "utilities"
)

func main() {

	// Initialize logger to output filename
    log.SetFlags(log.Lshortfile);
    // Initialize configuration constants
    var config *utilities.ProdConfig;
    config.InitializeConfig();

	var mysqlConnector *fin_database.MySqlConnector =  utilities.GetDefaultMysqlConnector();
    var waitGroup sync.WaitGroup;

    /*var newsInfoDatabase *fin_database.NewsInfoDatabase = fin_database.NewNewsInfoDatabase(
        utilities.DbType,
        "news_info",
        mysqlConnector);

    var newsContentDatabase *fin_database.NewsContentDatabase = fin_database.NewNewsContentDatabase(
        utilities.DbType,
        "news_content",
        mysqlConnector);

	var nytimesCrawler *NYTimesCrawler = NewNYTimesCrawler(
        &waitGroup,
        newsInfoDatabase,
        newsContentDatabase,
        2957, //startDayFromToday 
        5000, // endDayFromToday
        5, // maxPageDepthPerDay
        5 * 60 * 60, // updateFrequencySecs
        20); // waitSecsBeforeRestart
    crawlers := [...]Crawler{nytimesCrawler};
    var wsjCrawler *WSJCrawler = NewWSJCrawler(
        &waitGroup,
        newsInfoDatabase,
        newsContentDatabase,
        1131, // startDayFromToday
        5000, // endDayFromToday
        5 * 60 * 60, // updateFrequencySecs
        60); // waitSecsBeforeRestart
    crawlers := [...]Crawler{wsjCrawler};*/
    //crawlers := [...]Crawler{nytimesCrawler, wsjCrawler};

    /*json, err := ioutil.ReadFile("D:\\Users\\hungtantran\\PycharmProjects\\Models\\Rand\\NYTImes_response");
    if (err != nil) {
        log.Println(err);
        return;
    }
    content := string(json);
    nytimesCrawler.ParseOnePage(json);*/

    /*html, err := ioutil.ReadFile("D:\\Users\\hungtantran\\PycharmProjects\\Models\\Rand\\WSJ_response.html");
    if (err != nil) {
        log.Println(err);
        return;
    }
    content := string(html);
    wsjCrawler.ParseOnePage(content);*/

    var metricDatabase *fin_database.MetricDatabase = fin_database.NewMetricDatabase(
        utilities.DbType, mysqlConnector);
    var tickerInfoDatabase *fin_database.TickerInfoDatabase = fin_database.NewTickerInfoDatabase(
        utilities.DbType, "ticker_info", mysqlConnector);
    allTickerInfo := tickerInfoDatabase.GetAllTickerInfo();
    googleFinanceCrawler := NewGoogleFinanceCrawler(
        &waitGroup, metricDatabase, allTickerInfo, 20);
    crawlers := [...]Crawler{googleFinanceCrawler};

    /*html, err := ioutil.ReadFile("D:\\Users\\hungtantran\\PycharmProjects\\Models\\Rand\\google_finance_financial_html.txt");
    if (err != nil) {
        log.Println(err);
        return;
    }
    content := string(html);
    googleFinanceCrawler.ParseOnePage(content);*/

    for _, crawler := range(crawlers) {
        waitGroup.Add(1);
	    go crawler.Crawl();
    }
    waitGroup.Wait();
    log.Println("Done");
}