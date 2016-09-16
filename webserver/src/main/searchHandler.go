package main

import (
    "encoding/json"
    "log"
    "net/http"
    "net/url"
    "strings"
)

type SearchHandler interface {
    Search(r *http.Request) string 
}

type StandardSearchHandler struct {
    metricDatabase *MetricDatabase
}

func NewStandardSearchHandler(metricDatabase *MetricDatabase) *StandardSearchHandler {
    var searchHandler *StandardSearchHandler = new(StandardSearchHandler);
    searchHandler.metricDatabase = metricDatabase;
    return searchHandler;
}

func (searchHandler *StandardSearchHandler) Search(r *http.Request) string {
    var param url.Values = r.URL.Query();
    searchTypes, ok1 := param["type"];
    searchIds, ok2 := param["id"];

    tableName := "";
    var metricNames []string;
    if (ok1 && ok2 &&
        len(searchTypes) > 0 && searchTypes[0] != "" &&
        len(searchIds) > 0 && searchIds[0] != "0") {
        log.Println(searchTypes[0], searchIds[0]);

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
            log.Println(searchTerms[0]);
            if searchTypes[0] == "Equities" {
                tableName = searchTerms[0] + "_metrics";
                metricNames = append(metricNames, "adj_close");
                metricNames = append(metricNames, "volume");
            }
        }
    }

    log.Println(tableName, metricNames);
    if tableName != "" {
        var graph Graph;
        graph.Title = tableName
        graph.Plots = make(map[string]Plot);

        if len(metricNames) > 0 {
            for _, metricName := range metricNames {
                metrics := searchHandler.metricDatabase.getMetricWithName(tableName, metricName);
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
        return graphJsonString;
    }

    return ""
}