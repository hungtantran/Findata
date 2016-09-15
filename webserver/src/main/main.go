package main

import (
    "encoding/json"
	"fmt"
	"io/ioutil"
    "net/http"
    "net/url"
    "strings"
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

var allTickerInfo []TickerInfo
var allEconomicsInfo []EconomicsInfo
var metricDatabase *MetricDatabase;


func loadPage(title string) (string, error) {
    filename :=  "templates\\" + title + ".html"
    body, err := ioutil.ReadFile(filename)
    if err != nil {
        return "", err
    }
    return string(body), err
}

// TODO move each of the complicated handle like /search, /match
// to its own file 
// TODO move database classes to their own package

func indexHandler(w http.ResponseWriter, r *http.Request) {
    p, err := loadPage("index")
    if err != nil {
       p, err = loadPage("404")
    }
    fmt.Fprintf(w, p)
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
    var param url.Values = r.URL.Query();
    searchTypes, ok1 := param["type"];
    searchIds, ok2 := param["id"];

    tableName := "";
    var metricNames []string;
    if (ok1 && ok2 &&
        len(searchTypes) > 0 && searchTypes[0] != "" &&
        len(searchIds) > 0 && searchIds[0] != "0") {
        fmt.Println(searchTypes[0], searchIds[0]);

        if searchTypes[0] == "Equities" {
            tableName = strings.ToLower(searchIds[0]) + "_metrics";
            metricNames = append(metricNames, "adj_close");
            metricNames = append(metricNames, "volume");
        } else if searchTypes[0] == "Economics Indicators" {
            tableName = "economics_info_" + searchIds[0] + "_metrics";
        }
    } else {
        searchTerms, ok3 := param["term"];
        if (ok3 && len(searchTerms) > 0 && searchTerms[0] != "") {
            fmt.Println(searchTerms[0]);
            if searchTypes[0] == "Equities" {
                tableName = searchTerms[0] + "_metrics";
                metricNames = append(metricNames, "adj_close");
                metricNames = append(metricNames, "volume");
            }
        }
    }

    fmt.Println(tableName, metricNames);
    if tableName != "" {
        var graph Graph;
        graph.Title = tableName
        graph.Plots = make(map[string]Plot);

        if len(metricNames) > 0 {
            for _, metricName := range metricNames {
                metrics := metricDatabase.getMetricWithName(tableName, metricName);
                dataSet := DataSet {
                    Title: tableName,
                    Type: "line",
                    Data: metrics,
                }
                plot := Plot {
                    Title: tableName,
                    DataSets: map[string]DataSet {
                        metricName: dataSet,
                    },
                }
                graph.Plots[tableName + " " + metricName] = plot;
            }
        } else {
            // TODO here
        }

        graphJson, _ := json.Marshal(graph);
        graphJsonString := string(graphJson);
        fmt.Fprintf(w, graphJsonString);
    }
}

func matchHandler(w http.ResponseWriter, r *http.Request) {
    var param url.Values = r.URL.Query();
    matches, ok := param["match"]
    if !ok {
        fmt.Fprintf(w, "");
        return
    }

    allMatches := make(map[string][]MatchResult);
    // Find all metrics matches
    var count int = 0;
    var matchMetrics []MatchResult;
    for _, v := range allTickerInfo {
        if strings.HasPrefix(strings.ToUpper(v.name.String), strings.ToUpper(matches[0])) ||
           strings.Contains(strings.ToUpper(v.ticker.String), strings.ToUpper(matches[0])) {
            metadata := make(map[string]interface{});
            metadata["Id"] = v.ticker.String;
            matchResult := MatchResult{
                    Abbrv: v.ticker.String,
                    Name: v.name.String,
                    Metadata: metadata,}
            matchMetrics = append(matchMetrics, matchResult);
            count++;
            if (count >= maxNumMatchesReturned) {
                break;
            }
        }
    }

    if len(matchMetrics) > 0 {
        allMatches["Equities"] = matchMetrics;
    }

    // Find all economics info matches
    count = 0;
    var matchEonomicsInfo []MatchResult;
    for _, v := range allEconomicsInfo {
        // TODO don't convert upper everytime, precompute
        if strings.HasPrefix(strings.ToUpper(v.name.String), strings.ToUpper(matches[0])) ||
           strings.Contains(strings.ToUpper(v.name.String), strings.ToUpper(matches[0])) {
            metadata := make(map[string]interface{});
            metadata["Id"] = v.id.Int64;
            matchResult := MatchResult{
                    Abbrv: "",
                    Name: v.name.String,
                    Metadata: metadata,}
            matchEonomicsInfo = append(matchEonomicsInfo, matchResult);
            count++;
            if (count >= maxNumMatchesReturned) {
                break;
            }
        }
    }

    if len(matchEonomicsInfo) > 0 {
        allMatches["Economics Indicators"] = matchEonomicsInfo;
    }

    matchJsonString := "{}";
    matchJson, err := json.Marshal(allMatches);
    if err != nil {
        fmt.Println("error:", err)
    }
    matchJsonString = string(matchJson);
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
    // Initialize configuration constants
    var config *ProdConfig;
    config.initializeConfig();

    // Initialize the database connection objects
    var tickerInfoDatabase *TickerInfoDatabase = NewTickerInfoDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "");
    allTickerInfo = tickerInfoDatabase.getAllTickerInfo();

    var economicsInfoDatabase *EconomicsInfoDatabase = NewEconomicsInfoDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "economics_info");
    allEconomicsInfo = economicsInfoDatabase.getAllEconomicsInfo();

    metricDatabase = NewMetricDatabase(dbType,
        mysqlUsername,
        mysqlPassword,
        mysqlServer,
        mysqlDatabase,
        "");
}

func main() {
    go initializeConfiguration()

    http.HandleFunc("/about", aboutHandler)
    http.HandleFunc("/contact", contactHandler)
    http.HandleFunc("/search", searchHandler)
    http.HandleFunc("/match", matchHandler)
    http.HandleFunc("/", indexHandler)
    http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("static/css/"))))
    http.Handle("/generated/", http.StripPrefix("/generated/", http.FileServer(http.Dir("static/generated/"))))
    http.ListenAndServe(":8080", nil)
}
