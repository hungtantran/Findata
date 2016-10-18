package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "strconv"
)

type StandardSearchHandler struct {
    metricDatabase *MetricDatabase
    allTickerInfo []TickerInfo
    allEconomicsInfo []EconomicsInfo
    allExchangeIndexInfo []ExchangeIndexInfo
}

func NewStandardSearchHandler(
        metricDatabase *MetricDatabase,
        allTickerInfo []TickerInfo,
        allEconomicsInfo []EconomicsInfo,
        allExchangeIndexInfo []ExchangeIndexInfo) *StandardSearchHandler {
    var searchHandler *StandardSearchHandler = new(StandardSearchHandler);
    searchHandler.metricDatabase = metricDatabase;
    searchHandler.allEconomicsInfo = allEconomicsInfo;
    searchHandler.allTickerInfo = allTickerInfo;
    searchHandler.allExchangeIndexInfo = allExchangeIndexInfo;
    return searchHandler;
}

func (searchHandler *StandardSearchHandler) findTableAndMetricNames(param map[string]string) (string, []string) {
    tableName := "";
    var metricNames []string;
    searchType := param["type"];
    searchMetricType, err := strconv.Atoi(searchType);
    searchId := param["id"];
    searchTerm := param["term"];

    if (err == nil && searchId != "") {
        switch MetricType(searchMetricType) {
        case Equities:
            tableName = "ticker_info_" + searchId + "_metrics";
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

func (searchHandler *StandardSearchHandler) ProcessGetData(w http.ResponseWriter, param map[string]string) {
    tableName := param["tableName"];
    metricName := param["metricName"];

    metrics := searchHandler.metricDatabase.getMetricWithName(tableName, metricName);
    adjustedMetrics := searchHandler.adjustMetrics(metrics);
    metricsJson, _ := json.Marshal(adjustedMetrics);
    metricsJsonString := string(metricsJson);
    fmt.Fprintf(w, metricsJsonString);
}

func (searchHandler *StandardSearchHandler) ProcessGetGraph(w http.ResponseWriter, param map[string]string) {
    tableName, metricNames := searchHandler.findTableAndMetricNames(param);
    if tableName == "" {
        http.Error(w, "Error", 400);
        return;
    }

    var graph Graph;
    graph.Title = tableName;
    graph.Plots = make(map[string]Plot);

    for _, metricName := range metricNames {
        metricNameStr := metricName;
        if metricNameStr == "" {
            metricNameStr = tableName;
        }

        // TODO don't send down table name, only send down id
        dataDesc := make(map[string]string);
        dataDesc["metricName"] = metricName;
        dataDesc["tableName"] = tableName;
        dataSet := DataSet {
            Title: metricNameStr,
            Type: searchHandler.chooseChartType(tableName, metricName),
            DataDesc: dataDesc,
        }
        plot := Plot {
            Title: metricNameStr,
            DataSets: map[string]DataSet {
                metricName: dataSet,
            },
        }
        graph.Plots[metricNameStr] = plot;
    }

    graphJson, _ := json.Marshal(graph);
    graphJsonString := string(graphJson);
    fmt.Fprintf(w, graphJsonString);
}

func (searchHandler *StandardSearchHandler) ProcessPost(w http.ResponseWriter, r *http.Request) {
    var param map[string]string;
    err := json.NewDecoder(r.Body).Decode(&param)
    if err != nil {
        http.Error(w, "Error", 400);
        return;
    }

    action, ok := param["action"];
    if (!ok) {
        http.Error(w, "Error", 400);
        return;
    }

    switch action {
    case "GetGraph":
        searchHandler.ProcessGetGraph(w, param);
        return;
    case "GetData":
        searchHandler.ProcessGetData(w, param);
        return;
    default:
        log.Printf("Receive non-existing search action %s", action);
        http.Error(w, "Error", 400);
        return;
    }
}

func (searchHandler *StandardSearchHandler) ProcessGet(w http.ResponseWriter, r *http.Request) {
    http.Error(w, "Error", 400);
}

func (searchHandler *StandardSearchHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        page, _ := loadPage("404");
        fmt.Fprintf(w, page);
    case "POST":
        searchHandler.ProcessPost(w, r);
    default:
        page, _ := loadPage("404");
        fmt.Fprintf(w, page);
    }
}