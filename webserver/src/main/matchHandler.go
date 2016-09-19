package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "net/url"
    "strings"
)

type StandardMatchHandler struct {
    allTickerInfo []TickerInfo
    allEconomicsInfo []EconomicsInfo
    allExchangeIndexInfo []ExchangeIndexInfo
}

func NewStandardMatchHandler(
        allTickerInfo []TickerInfo,
        allEconomicsInfo []EconomicsInfo,
        allExchangeIndexInfo []ExchangeIndexInfo) *StandardMatchHandler {
    var matchHandler *StandardMatchHandler = new(StandardMatchHandler);
    matchHandler.allEconomicsInfo = allEconomicsInfo;
    matchHandler.allTickerInfo = allTickerInfo;
    matchHandler.allExchangeIndexInfo = allExchangeIndexInfo;
    return matchHandler;
}

func (matchHandler *StandardMatchHandler) StringMatchPart(matchString string, fullString string) bool {
    match := true;
    
    matchParts := strings.Split(matchString, " ");
    for _, part := range matchParts {
        if !strings.Contains(fullString, part) {
            match = false;
        }
    }

    return match;
}

func (matchHandler *StandardMatchHandler) ProcessGet(w http.ResponseWriter, r *http.Request) {
    var param url.Values = r.URL.Query();
    matches, ok := param["match"];
    if !ok {
        fmt.Fprintf(w, "");
        return;
    }

    allMatches := make(map[MetricType][]MatchResult);
    upperMatch := strings.ToUpper(matches[0]);
    // Find all metrics matches
    var count int = 0;
    var matchIndices []MatchResult;
    for _, v := range matchHandler.allExchangeIndexInfo {
        upperName := strings.ToUpper(v.Name.String);
        upperIndex := strings.ToUpper(v.Index.String);
        if (strings.HasPrefix(upperIndex, upperMatch) || matchHandler.StringMatchPart(upperMatch, upperName)) {
            metadata := make(map[string]interface{});
            metadata["Id"] = v.Id.Int64;
            matchResult := MatchResult{
                    Abbrv: v.Index.String,
                    Name: v.Name.String,
                    Metadata: metadata,}
            matchIndices = append(matchIndices, matchResult);
            count++;
            if (count >= maxNumMatchesReturned) {
                break;
            }
        }
    }

    if len(matchIndices) > 0 {
        allMatches[Indices] = matchIndices;
    }

    // Find all metrics matches
    count = 0;
    var matchMetrics []MatchResult;
    for _, v := range matchHandler.allTickerInfo {
        upperName := strings.ToUpper(v.name.String);
        upperTicker := strings.ToUpper(v.ticker.String);
        if (strings.HasPrefix(upperTicker, upperMatch) || matchHandler.StringMatchPart(upperMatch, upperName)) {
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
        allMatches[Equities] = matchMetrics;
    }

    // Find all economics info matches
    count = 0;
    var matchEonomicsInfo []MatchResult;
    for _, v := range matchHandler.allEconomicsInfo {
        upperName := strings.ToUpper(v.name.String);
        if matchHandler.StringMatchPart(upperMatch, upperName) {
            metadata := make(map[string]interface{});
            metadata["Id"] = v.id.Int64;
            metadata["Ca"] = v.category.String;
            metadata["Ty"] = v.typeStr.String;
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
        allMatches[EconIndicator] = matchEonomicsInfo;
    }

    matchJsonString := "{}";
    matchJson, err := json.Marshal(allMatches);
    if err != nil {
        log.Println("error:", err)
    }
    matchJsonString = string(matchJson);
    fmt.Fprintf(w, matchJsonString)
}

func (matchHandler *StandardMatchHandler) Process(w http.ResponseWriter, r *http.Request) {
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