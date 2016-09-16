package main

import (
	"fmt"
	"io/ioutil"
    "log"
    "net/http"
    "os"
)


type MatchResult struct {
    Abbrv string 
    Name string
    Metadata map[string]interface{}
}

type DataSet struct {
    Title string
    Type string
    Data []ResultMetric
}

type Plot struct {
    Title string
    DataSets map[string]DataSet
}

type Graph struct {
    Title string
    Plots map[string]Plot
}

var metricDatabase *MetricDatabase;
var searchHandlerObj SearchHandler;
var matchHandlerObj MatchHandler;


func loadPage(title string) (string, error) {
    filename :=  "templates" + string(os.PathSeparator) + title + ".html"
    body, err := ioutil.ReadFile(filename)
    if err != nil {
        return "", err
    }
    return string(body), err
}

// TODO move database classes to their own package

func indexHandler(w http.ResponseWriter, r *http.Request) {
    p, err := loadPage("index")
    if err != nil {
       p, err = loadPage("404")
    }
    fmt.Fprintf(w, p)
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
    graphJsonString := searchHandlerObj.Search(r);
    fmt.Fprintf(w, graphJsonString);
}

func matchHandler(w http.ResponseWriter, r *http.Request) {
    matchJsonString := matchHandlerObj.Match(r);
    fmt.Fprintf(w, matchJsonString);
}

func aboutHandler(w http.ResponseWriter, r *http.Request) {
    p, err := loadPage("about")
    if err != nil {
       p, err = loadPage("404")
    }
    fmt.Fprintf(w, p)
}

func contactHandler(w http.ResponseWriter, r *http.Request) {
    p, err := loadPage("contact")
    if err != nil {
       p, err = loadPage("404")
    }
    fmt.Fprintf(w, p)
}

func initializeConfiguration() {
    // Initialize logger to output filename
    log.SetFlags(log.Lshortfile);
    
    // Initialize configuration constants
    var config *ProdConfig;
    config.initializeConfig();

    // Initialize match handler
    var tickerInfoDatabase *TickerInfoDatabase = NewTickerInfoDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "");
    allTickerInfo := tickerInfoDatabase.getAllTickerInfo();

    var economicsInfoDatabase *EconomicsInfoDatabase = NewEconomicsInfoDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "economics_info");
    allEconomicsInfo := economicsInfoDatabase.getAllEconomicsInfo();

    matchHandlerObj = NewStandardMatchHandler(allTickerInfo, allEconomicsInfo);
    
    // Initialize search handler
    metricDatabase = NewMetricDatabase(dbType,
        mysqlUsername,
        mysqlPassword,
        mysqlServer,
        mysqlDatabase,
        "");
    searchHandlerObj = NewStandardSearchHandler(metricDatabase);
}

func main() {
    go initializeConfiguration();

    http.HandleFunc("/about", aboutHandler);
    http.HandleFunc("/contact", contactHandler);
    http.HandleFunc("/search", searchHandler);
    http.HandleFunc("/match", matchHandler);
    http.HandleFunc("/", indexHandler);
    http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("static/css/"))));
    http.Handle("/generated/", http.StripPrefix("/generated/", http.FileServer(http.Dir("static/generated/"))));
    http.ListenAndServe(httpAddressAndPort, nil);
}
