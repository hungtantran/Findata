package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "strconv"
    "time"
    "os"
    "strings"
    "bytes"
    "io/ioutil"
    elastic "gopkg.in/olivere/elastic.v3"
    //"github.com/davecgh/go-spew/spew"

    "fin_database"
    "utilities"
)

type ElasticSearchHistogramJsonObject struct {
	Aggregations AggregationsObject
}

type AggregationsObject struct {
	Articles_over_time Articles_over_timeObject
}

type Articles_over_timeObject struct {
	Buckets []BucketObject
}

type BucketObject struct {
	Key_as_string string
    Doc_count int
}

type DataDesc struct {
    TableName string
    TableCode string
    DataType MetricType
    MetricDescs []MetricDesc
}

type MetricDesc struct {
    MetricName string
    MetricCode string
}

type StandardSearchHandler struct {
    metricDatabase *fin_database.MetricDatabase
    allTickerInfo map[int64]fin_database.TickerInfo
    allEconomicsInfo map[int64]fin_database.EconomicsInfo
    allExchangeIndexInfo map[int64]fin_database.ExchangeIndexInfo
    elasticClient *elastic.Client
}

func NewStandardSearchHandler(
        metricDatabase *fin_database.MetricDatabase,
        allTickerInfo map[int64]fin_database.TickerInfo,
        allEconomicsInfo map[int64]fin_database.EconomicsInfo,
        allExchangeIndexInfo map[int64]fin_database.ExchangeIndexInfo,
        elasticSearchIp string,
        elasticSearchPort int) *StandardSearchHandler {
    var connectionString string = elasticSearchIp + ":" + fmt.Sprintf("%d", elasticSearchPort);
    elasticClient, err := elastic.NewClient(
        elastic.SetURL(connectionString),
        elastic.SetSniff(false),
        elastic.SetHealthcheckInterval(10*time.Second),
        elastic.SetMaxRetries(5),
        elastic.SetErrorLog(log.New(os.Stderr, "ELASTIC ", log.LstdFlags)));
        //elastic.SetInfoLog(log.New(os.Stdout, "", log.LstdFlags)))
	if err != nil {
		// Handle error
		panic(err)
	}

    var searchHandler *StandardSearchHandler = new(StandardSearchHandler);
    searchHandler.metricDatabase = metricDatabase;
    searchHandler.allEconomicsInfo = allEconomicsInfo;
    searchHandler.allTickerInfo = allTickerInfo;
    searchHandler.allExchangeIndexInfo = allExchangeIndexInfo;
    searchHandler.elasticClient = elasticClient;

    return searchHandler;
}

func (searchHandler *StandardSearchHandler) findMetrics(param map[string]string) ([]DataDesc) {
    var metrics []DataDesc;

    searchType := param["type"];
    // TODO check error
    searchMetricType, err := strconv.Atoi(searchType);
    searchId, err := strconv.ParseInt(param["id"], 10, 64);
    searchTerm := param["term"];

    if (err == nil) {
        switch MetricType(searchMetricType) {
        case Equities:
            tableCode := fmt.Sprintf("ticker_info_%d_metrics", searchId);
            adjClose := MetricDesc{
                MetricName: "Adjusted Close",
                MetricCode: "adj_close",
            };
            volume := MetricDesc{
                MetricName: "Volume",
                MetricCode: "volume",
            };
            metricDesc := []MetricDesc{adjClose, volume};
            dataDesc := DataDesc{
                TableName: searchHandler.allTickerInfo[searchId].Name.String,
                TableCode: tableCode,
                MetricDescs: metricDesc,
            };
            metrics = append(metrics, dataDesc);
        case EconIndicator:
            tableCode := fmt.Sprintf("economics_info_%d_metrics", searchId);
            econMetric := MetricDesc{
                MetricName: searchHandler.allEconomicsInfo[searchId].Name.String,
                MetricCode: "",
            };
            metricDesc := []MetricDesc{econMetric};
            dataDesc := DataDesc{
                TableName: searchHandler.allTickerInfo[searchId].Name.String,
                TableCode: tableCode,
                MetricDescs: metricDesc,
            };
            metrics = append(metrics, dataDesc);
        case Indices:
            tableCode := fmt.Sprintf("exchange_index_info_%d_metrics", searchId);
            adjClose := MetricDesc{
                MetricName: "Adjusted Close",
                MetricCode: "adj_close",
            };
            volume := MetricDesc{
                MetricName: "Volume",
                MetricCode: "volume",
            };
            metricDesc := []MetricDesc{adjClose, volume};
            dataDesc := DataDesc{
                TableName: searchHandler.allExchangeIndexInfo[searchId].Name.String,
                TableCode: tableCode,
                MetricDescs: metricDesc,
            };
            metrics = append(metrics, dataDesc);
        }
    } else {
        tableCode := "news_info";
        newsInfoMetric := MetricDesc{
            MetricName: searchTerm,
            MetricCode: searchTerm,
        };
        metricDesc := []MetricDesc{newsInfoMetric};
        dataDesc := DataDesc{
            TableName: "Count of term in news articles",
            TableCode: tableCode,
            MetricDescs: metricDesc,
        };
        metrics = append(metrics, dataDesc);
    }

    return metrics;
}

func (searchHandler *StandardSearchHandler) chooseChartType(tableName string, metricName string) string {
    if metricName == "volume" {
        return "bar";
    }
    return "line";
}

func (searchHandler *StandardSearchHandler) adjustMetrics(metrics []fin_database.ResultMetric) []fin_database.ResultMetric {
    const maxDetailedPoint int = 300;
    const maxSparsePoint int = 300;

    if len(metrics) > maxDetailedPoint {
        var adjustedMetrics []fin_database.ResultMetric;
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

func (searchHandler *StandardSearchHandler) GetNewsInfoData(match string) []fin_database.ResultMetric {
    matchParts := strings.Split(match, " ");
    var matchStr string;
    for index, matchPart := range matchParts {
        if (index < len(matchParts) - 1) {
            matchStr += fmt.Sprintf(`{ "match": { "headline": "%s" }},`, matchPart);
        } else {
            matchStr += fmt.Sprintf(`{ "match": { "headline": "%s" }}`, matchPart);
        }
    }

    queryString := []byte(fmt.Sprintf(`{
        "size": 0,
        "query" : {
            "bool": {
                "must": [%s]
            }
        },
        "aggs" : {
            "articles_over_time" : {
                "date_histogram" : {
                    "field" : "date",
                    "interval" : "1w"
                }
            }
        }
    }`, matchStr));

    var connectionString string = fmt.Sprintf(
        "http://%s:%d/news/news_info/_search",
        utilities.ElasticSearchIp,
        utilities.ElasticSearchPort);
    req, err := http.NewRequest("POST", connectionString, bytes.NewBuffer(queryString));
    req.Header.Set("Content-Type", "application/json");
    client := &http.Client{};
    resp, err := client.Do(req);
    defer resp.Body.Close();

    var histogramObject ElasticSearchHistogramJsonObject;
    body, err := ioutil.ReadAll(resp.Body);
    json.Unmarshal(body, &histogramObject);
    //spew.Dump(histogramObject);

    var allMetric []fin_database.ResultMetric;
    buckets := histogramObject.Aggregations.Articles_over_time.Buckets;
    for _, bucket := range(buckets) {
        var dateString string = bucket.Key_as_string;
        var metric fin_database.ResultMetric;
        date, _ := time.Parse("2006-01-02 15:04:05", dateString);
        metric.T = date;
        metric.V = float64(bucket.Doc_count);
        allMetric = append(allMetric, metric);
    }

    if err != nil {
        log.Println(err);
        return allMetric;
    }
    return allMetric;
}

func (searchHandler *StandardSearchHandler) ProcessGetData(w http.ResponseWriter, param map[string]string) {
    tableCode := param["tableCode"];
    metricCode := param["metricCode"];

    // news_info is special "fake" table that will get data from elasticsearch
    var metrics []fin_database.ResultMetric;
    if (tableCode == "news_info") {
        metrics = searchHandler.GetNewsInfoData(metricCode);
    } else {
        metrics = searchHandler.metricDatabase.GetMetricWithName(
            tableCode, metricCode);
    }

    adjustedMetrics := searchHandler.adjustMetrics(metrics);
    metricsJson, _ := json.Marshal(adjustedMetrics);
    metricsJsonString := string(metricsJson);

    fmt.Fprintf(w, metricsJsonString);
}

func (searchHandler *StandardSearchHandler) ProcessGetGraph(w http.ResponseWriter, param map[string]string) {
    metrics := searchHandler.findMetrics(param);
    graphJson, _ := json.Marshal(metrics);
    graphJsonString := string(graphJson);
    log.Printf("%s\n", graphJsonString);
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