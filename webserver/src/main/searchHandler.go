package main

import (
    "encoding/json"
    "log"
    "net/http"
    "strings"
    "strconv"
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

func (searchHandler *StandardSearchHandler) findTableAndMetricNames(r *http.Request) (string, []string) {
    tableName := "";
    var metricNames []string;

    var param map[string]string;
    err := json.NewDecoder(r.Body).Decode(&param)
    if err != nil {
        return tableName, metricNames;
    }

    searchType := param["type"];
    searchMetricType, err := strconv.Atoi(searchType);
    searchId := param["id"];
    searchTerm := param["term"];

    if (err == nil && searchId != "") {
        switch MetricType(searchMetricType) {
        case Equities:
            tableName = strings.ToLower(searchId) + "_metrics";
            metricNames = append(metricNames, "adj_close");
            metricNames = append(metricNames, "volume");
        case EconIndicator:
            tableName = "economics_info_" + searchId + "_metrics";
        case Indices:
            tableName = "exchange_index_info_" + searchId + "_metrics";
            metricNames = append(metricNames, "adj_close");
            metricNames = append(metricNames, "volume");
        }
    } else if (searchTerm != "") {
        tableName = searchTerm + "_metrics";
        metricNames = append(metricNames, "adj_close");
        metricNames = append(metricNames, "volume");
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
    tableName, metricNames := searchHandler.findTableAndMetricNames(r);

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