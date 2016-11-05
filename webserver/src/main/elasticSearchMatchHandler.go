package main

import (
    "encoding/json"
    "errors"
    "fmt"
    "log"
    "net/http"
    "net/url"
    "os"
    "strings"
    "time"
    elastic "gopkg.in/olivere/elastic.v3"
)

type ElasticSearchMatchHandler struct {
    client *elastic.Client
}

func NewElasticSearchMatchHandler(elasticSearchIp string, elasticSearchPort int) *ElasticSearchMatchHandler {
    var connectionString string = elasticSearchIp + ":" + fmt.Sprintf("%d", elasticSearchPort);
    client, err := elastic.NewClient(
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

    var matchHandler *ElasticSearchMatchHandler = new(ElasticSearchMatchHandler);
    matchHandler.client = client;
    return matchHandler;
}

func (matchHandler *ElasticSearchMatchHandler) FindTickerInfoMatches(match string) ([]MatchResult, error) {
    matchParts := strings.Split(match, " ");
    var queries []elastic.Query;
    for _, matchPart := range matchParts {
        queries = append(queries, elastic.NewPrefixQuery("name", matchPart));
    }
    nameQuery := elastic.NewBoolQuery();
    nameQuery = nameQuery.Must(queries...);

    query := elastic.NewBoolQuery();
    query = query.Should(
        nameQuery,
        elastic.NewPrefixQuery("ticker", match));
    searchResult, err := matchHandler.client.Search().
        Index("findata").
        Type("ticker_info").
        Field("id").
        Field("ticker").
        Field("name").
        Query(query).
        From(0).Size(10).
        Pretty(true).
        Do();
    if err != nil {
        return nil, errors.New("Can't query elasticsearch");
    }

    var matchTickerInfo []MatchResult;
    if searchResult.Hits.TotalHits > 0 {
        // Iterate through results
        for _, hit := range searchResult.Hits.Hits {
            var result map[string]interface{} = hit.Fields;
            ids, _ := result["id"].([]interface{});
            names, _ := result["name"].([]interface{});
            tickers, _ := result["ticker"].([]interface{});
            id := int(ids[0].(float64));
            name := names[0].(string);
            ticker := tickers[0].(string);

            metadata := make(map[string]interface{});
            metadata["Id"] = id;
            matchResult := MatchResult{
                Abbrv: ticker,
                Name: name,
                Metadata: metadata,
            }
            matchTickerInfo = append(matchTickerInfo, matchResult);
        }
    }

    return matchTickerInfo, nil;
}

func (matchHandler *ElasticSearchMatchHandler) FindExchangeIndexInfoMatches(match string) ([]MatchResult, error) {
    matchParts := strings.Split(match, " ");
    var queries []elastic.Query;
    for _, matchPart := range matchParts {
        queries = append(queries, elastic.NewPrefixQuery("name", matchPart));
    }
    nameQuery := elastic.NewBoolQuery();
    nameQuery = nameQuery.Must(queries...);

    query := elastic.NewBoolQuery();
    query = query.Should(
        nameQuery,
        elastic.NewPrefixQuery("index", match));
    searchResult, err := matchHandler.client.Search().
        Index("findata").
        Type("exchange_index_info").
        Field("id").
        Field("index").
        Field("name").
        Query(query).
        From(0).Size(10).
        Pretty(true).
        Do();
    if err != nil {
        return nil, errors.New("Can't query elasticsearch");
    }

    var matchExchangeIndexInfo []MatchResult;
    if searchResult.Hits.TotalHits > 0 {
        // Iterate through results
        for _, hit := range searchResult.Hits.Hits {
            var result map[string]interface{} = hit.Fields;
            ids, _ := result["id"].([]interface{});
            names, _ := result["name"].([]interface{});
            indices, _ := result["index"].([]interface{});
            id := int(ids[0].(float64));
            name := names[0].(string);
            index := indices[0].(string);

            metadata := make(map[string]interface{});
            metadata["Id"] = id;
            matchResult := MatchResult{
                Abbrv: index,
                Name: name,
                Metadata: metadata,
            }
            matchExchangeIndexInfo = append(matchExchangeIndexInfo, matchResult);
        }
    }

    return matchExchangeIndexInfo, nil;
}

func (matchHandler *ElasticSearchMatchHandler) FindEconomicsInfoMatches(match string) ([]MatchResult, error) {
    matchParts := strings.Split(match, " ");
    var nameQueries, categoryQueries, typeQueries []elastic.Query;
    for _, matchPart := range matchParts {
        nameQueries = append(nameQueries, elastic.NewPrefixQuery("name", matchPart));
        categoryQueries = append(categoryQueries, elastic.NewPrefixQuery("category", matchPart));
        typeQueries = append(typeQueries, elastic.NewPrefixQuery("type", matchPart));
    }
    nameQuery := elastic.NewBoolQuery();
    categoryQuery := elastic.NewBoolQuery();
    typeQuery := elastic.NewBoolQuery();
    nameQuery = nameQuery.Must(nameQueries...);
    categoryQuery = categoryQuery.Must(categoryQueries...);
    typeQuery = typeQuery.Must(typeQueries...);

    query := elastic.NewBoolQuery();
    query = query.Should(
        nameQuery,
        categoryQuery,
        typeQuery);
    searchResult, err := matchHandler.client.Search().
        Index("findata").
        Type("economics_info").
        Field("id").
        Field("name").
        Field("category").
        Field("type").
        Query(query).
        From(0).Size(10).
        Pretty(true).
        Do();
    if err != nil {
        return nil, errors.New("Can't query elasticsearch");
    }

    var matchEconomicsInfo []MatchResult;
    if searchResult.Hits.TotalHits > 0 {
        // Iterate through results
        for _, hit := range searchResult.Hits.Hits {
            var result map[string]interface{} = hit.Fields;
            ids, _ := result["id"].([]interface{});
            names, _ := result["name"].([]interface{});
            categories, _ := result["category"].([]interface{});
            types, _ := result["type"].([]interface{});
            id := int(ids[0].(float64));
            name := names[0].(string);
            category := categories[0].(string);
            typeStr := types[0].(string);

            metadata := make(map[string]interface{});
            metadata["Id"] = id;
            metadata["Ca"] = category;
            metadata["Ty"] = typeStr;
            matchResult := MatchResult{
                Abbrv: "",
                Name: name,
                Metadata: metadata,
            }
            matchEconomicsInfo = append(matchEconomicsInfo, matchResult);
        }
    }

    return matchEconomicsInfo, nil;
}

func (matchHandler *ElasticSearchMatchHandler) ProcessGet(w http.ResponseWriter, r *http.Request) {
    var param url.Values = r.URL.Query();
    matches, ok := param["match"];
    if !ok {
        fmt.Fprintf(w, "");
        return;
    }

    match := matches[0];
    allMatches := make(map[MetricType][]MatchResult);

    // Find all exchange index info matches
    exchangeIndexInfoMatches, err := matchHandler.FindExchangeIndexInfoMatches(match);
    if (err != nil) {
        fmt.Println("error");
        exchangeIndexInfoMatches = nil;
        return;
    }
    if (exchangeIndexInfoMatches != nil && len(exchangeIndexInfoMatches) > 0) {
        allMatches[Indices] = exchangeIndexInfoMatches;
    }

    // Find all ticker info matches
    tickerInfoMatches, err := matchHandler.FindTickerInfoMatches(match);
    if (err != nil) {
        fmt.Println("error");
        tickerInfoMatches = nil;
        return;
    }
    if (tickerInfoMatches != nil && len(tickerInfoMatches) > 0) {
        allMatches[Equities] = tickerInfoMatches;
    }

    // Find all economics info matches
    economicsInfoMatches, err := matchHandler.FindEconomicsInfoMatches(match);
    if (err != nil) {
        fmt.Println("error");
        economicsInfoMatches = nil;
        return;
    }
    if (economicsInfoMatches != nil && len(economicsInfoMatches) > 0) {
        allMatches[EconIndicator] = economicsInfoMatches;
    }

    matchJsonString := "{}";
    matchJson, err := json.Marshal(allMatches);
    if err != nil {
        log.Println("error:", err)
    }
    matchJsonString = string(matchJson);
    fmt.Fprintf(w, matchJsonString)
}

func (matchHandler *ElasticSearchMatchHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        matchHandler.ProcessGet(w, r);
    case "POST":
        page, _ := loadPage("404");
        fmt.Fprintf(w, page);
    default:
        page, _ := loadPage("404");
        fmt.Fprintf(w, page);
    }
}