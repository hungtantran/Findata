package main

import (
    "encoding/json"
    "log"
    "net/http"
    "net/url"
    "strings"
)

type MatchHandler interface {
    Match(r *http.Request) string 
}

type StandardMatchHandler struct {
    allTickerInfo []TickerInfo
    allEconomicsInfo []EconomicsInfo
}

func NewStandardMatchHandler(allTickerInfo []TickerInfo, allEconomicsInfo []EconomicsInfo) *StandardMatchHandler {
    var matchHandler *StandardMatchHandler = new(StandardMatchHandler);
    matchHandler.allEconomicsInfo = allEconomicsInfo;
    matchHandler.allTickerInfo = allTickerInfo;
    return matchHandler;
}

func (matchHandler *StandardMatchHandler) Match(r *http.Request) string {
    var param url.Values = r.URL.Query();
    matches, ok := param["match"];
    if !ok {
        return "";
    }

    allMatches := make(map[string][]MatchResult);
    // Find all metrics matches
    var count int = 0;
    var matchMetrics []MatchResult;
    for _, v := range matchHandler.allTickerInfo {
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
    for _, v := range matchHandler.allEconomicsInfo {
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
        log.Println("error:", err)
    }
    matchJsonString = string(matchJson);
    return matchJsonString;
}