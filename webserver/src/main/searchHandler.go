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

func (searchHandler *StandardSearchHandler) findTableAndMetricNames(param url.Values) (string, []string) {
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
            tableName = searchTerms[0] + "_metrics";
            metricNames = append(metricNames, "adj_close");
            metricNames = append(metricNames, "volume");
        }
    }

    if len(metricNames) == 0 {
        metricNames = append(metricNames, "");
    }

    log.Println(tableName, metricNames);
    return tableName, metricNames;
}

func (searchHandler *StandardSearchHandler) chooseChartType(tableName string, metricName string) string {
    if metricName == "volume" {
        return "bar";
    }
    return "line";
}

func (searchHandler *StandardSearchHandler) adjustMetrics(metrics []ResultMetric) []ResultMetric {
    const maxDetailedPoint int = 300;
    const maxSparsePoint int = 300;

    if len(metrics) > maxDetailedPoint {
        var adjustedMetrics []ResultMetric;
        var step int;
        step = (len(metrics) - maxDetailedPoint) / maxSparsePoint;
        if step < 1 {
            step = 1;
        }
        for i := 0; i < len(metrics) - maxDetailedPoint; i+=step {
            adjustedMetrics = append(adjustedMetrics, metrics[i]); 
        }
        adjustedMetrics = append(adjustedMetrics, metrics[len(metrics) - maxDetailedPoint:]...);
        return adjustedMetrics;
    } else {
        return metrics;
    }
}

func (searchHandler *StandardSearchHandler) Search(r *http.Request) string {
    var param url.Values = r.URL.Query();
    tableName, metricNames := searchHandler.findTableAndMetricNames(param);

    if tableName != "" {
        var graph Graph;
        graph.Title = tableName
        graph.Plots = make(map[string]Plot);

        for _, metricName := range metricNames {
            metrics := searchHandler.metricDatabase.getMetricWithName(tableName, metricName);
            adjustedMetrics := searchHandler.adjustMetrics(metrics);

            dataSet := DataSet {
                Title: tableName,
                Type: searchHandler.chooseChartType(tableName, metricName),
                Data: adjustedMetrics,
            }
            plot := Plot {
                Title: tableName,
                DataSets: map[string]DataSet {
                    metricName: dataSet,
                },
            }
            graph.Plots[tableName + " " + metricName] = plot;
        }

        graphJson, _ := json.Marshal(graph);
        graphJsonString := string(graphJson);
        return graphJsonString;
    }

    return ""
}