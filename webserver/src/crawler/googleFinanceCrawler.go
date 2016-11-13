package main

import (
    "bytes"
    "errors"
    "regexp"
    "fmt"
    "sync"
    "io/ioutil"
    "log"
    "net/http"
    "strings"
    "strconv"
    "time"
    //"github.com/davecgh/go-spew/spew"
    "golang.org/x/net/html"

    "fin_database"
    "utilities"
)

var GOOGLE_FINANCE_API string = "https://www.google.com/finance?q=%s%%3A%s&fstype=ii";

type GoogleFinanceCrawler struct {
    waitGroup *sync.WaitGroup
    metricDatabase *fin_database.MetricDatabase
    allTickerInfo []fin_database.TickerInfo
    updateFrequencySecs int
}

func NewGoogleFinanceCrawler(
        waitGroup *sync.WaitGroup,
        metricDatabase *fin_database.MetricDatabase,
        allTickerInfo []fin_database.TickerInfo,
        updateFrequencySecs int) *GoogleFinanceCrawler {
    var googleFinanceCrawler *GoogleFinanceCrawler = new(GoogleFinanceCrawler);
    googleFinanceCrawler.waitGroup = waitGroup;
    googleFinanceCrawler.metricDatabase = metricDatabase;
    googleFinanceCrawler.allTickerInfo = allTickerInfo;
    googleFinanceCrawler.updateFrequencySecs = updateFrequencySecs;
    return googleFinanceCrawler;
}

func (googleFinanceCrawler *GoogleFinanceCrawler) Crawl() {
    count := 0;
    for _, ticker := range googleFinanceCrawler.allTickerInfo {
        if (ticker.TickerType.String == "stock" && ticker.Exchange.Valid &&
            ticker.Ticker.Valid && utilities.IsStringAlphabet(ticker.Ticker.String)) {
            count++;
            log.Printf("Process %d ticker info", count);
            err := googleFinanceCrawler.CrawlOneTry(&ticker);
            if (err != nil) {
                log.Println(err);
                googleFinanceCrawler.waitGroup.Done();
                return;
            }
        }
        time.Sleep(time.Duration(googleFinanceCrawler.updateFrequencySecs) * time.Second);
    }
    googleFinanceCrawler.waitGroup.Done();
}

func (googleFinanceCrawler *GoogleFinanceCrawler) CrawlOneTry(ticker *fin_database.TickerInfo) error {
    abbr := ticker.Ticker.String;
    exchange := ticker.Exchange.String;
    log.Printf("Crawl ticker %s (%s)", abbr, exchange);
    tickerLink := fmt.Sprintf(GOOGLE_FINANCE_API, abbr, exchange);
    log.Printf("Crawl google finance for link %s", tickerLink);

    resp, err := http.Get(tickerLink);
    if (err != nil) {
        return errors.New("Exceed max num error");
    }
    defer resp.Body.Close();
    body, err := ioutil.ReadAll(resp.Body);
    var metrics []fin_database.Metric = googleFinanceCrawler.ParseOnePage(string(body));
    log.Printf("Insert %d metrics", len(metrics));
    for _, metric := range(metrics) {
        tableName := fmt.Sprintf("ticker_info_%d_metrics", ticker.Id.Int64);
        googleFinanceCrawler.metricDatabase.InsertMetric(tableName, &metric);
    }
    return nil;
}

func (googleFinanceCrawler *GoogleFinanceCrawler) ParseOnePage(content string) []fin_database.Metric {
    var metrics []fin_database.Metric;
    reader := bytes.NewBufferString(content)
    doc, err := html.Parse(reader)
    if err != nil {
        log.Println("Can't parse google finance html");
        return metrics;
    }

    var contentNodes []*html.Node;
    attrKeys := []string{"id"};
    attrValues := []string{"incinterimdiv"};
    utilities.ExtractItemsFromNode(
        doc, "div", attrKeys, attrValues, &contentNodes);

    attrValues[0] = "incannualdiv";
    utilities.ExtractItemsFromNode(
        doc, "div", attrKeys, attrValues, &contentNodes);

    attrValues[0] = "balinterimdiv";
    utilities.ExtractItemsFromNode(
        doc, "div", attrKeys, attrValues, &contentNodes);

    attrValues[0] = "balannualdiv";
    utilities.ExtractItemsFromNode(
        doc, "div", attrKeys, attrValues, &contentNodes);

    attrValues[0] = "casinterimdiv";
    utilities.ExtractItemsFromNode(
        doc, "div", attrKeys, attrValues, &contentNodes);

    attrValues[0] = "casannualdiv";
    utilities.ExtractItemsFromNode(
        doc, "div", attrKeys, attrValues, &contentNodes);
    if (len(contentNodes) != 6) {
        log.Printf("Only find %d content nodes", len(contentNodes));
    }

    for _, node := range(contentNodes) {
        err = nil;
        var emptyAttrKeys []string;
        var emptyAttrValues []string;
        var headerNodes []*html.Node;

        // Parse the header
        utilities.ExtractItemsFromNode(node, "th", emptyAttrKeys, emptyAttrValues, &headerNodes);
        var startDates []time.Time;
        var endDates []time.Time;
        for _, headerNode := range(headerNodes) {
            header := strings.TrimSpace(utilities.ExtractFirstTextFromNode(headerNode));
            startDate, endDate, err := googleFinanceCrawler.ParseHeaderToDates(header);
            if (err != nil) {
                log.Println(header);
                log.Println(err);
                continue;
            }
            startDates = append(startDates, *startDate);
            endDates = append(endDates, *endDate);
        }

        // Parse the content
        var rowNodes []*html.Node;
        utilities.ExtractItemsFromNode(node, "tr", emptyAttrKeys, emptyAttrValues, &rowNodes);
        for _, rowNode := range(rowNodes) {
            var cellNodes []*html.Node;
            utilities.ExtractItemsFromNode(rowNode, "td", emptyAttrKeys, emptyAttrValues, &cellNodes);
            if (len(cellNodes) != len(startDates) + 1) {
                continue;
            }

            cellTitle := strings.TrimSpace(utilities.ExtractFirstTextFromNode(cellNodes[0]));
            for i, cell := range(cellNodes) {
                if (i == 0) {
                    continue;
                }
                valStr := strings.Replace(utilities.ExtractFirstTextFromNode(cell), ",", "", -1);
                negative := false;
                if (len(valStr) > 0 && valStr[0] == '-') {
                    valStr = valStr[1:];
                    negative = true;
                }
                val, err := strconv.ParseFloat(valStr, 32);
                if (negative) {
                    val = -val;
                }
                if (err != nil) {
                    continue;
                }
                var metric fin_database.Metric;
                metric.MetricName.String = cellTitle;
                metric.MetricName.Valid = true; 
                metric.Value.Float64 = val;
                metric.Value.Valid = true;
                metric.StartDate = startDates[i-1];
                metric.EndDate = endDates[i-1];
                metrics = append(metrics, metric);
            }
        }
    }

    //spew.Dump(metrics);

    return metrics;
}

func (googleFinanceCrawler *GoogleFinanceCrawler) ParseHeaderToDates(header string) (*time.Time, *time.Time, error) {
    err := errors.New("Parsing error");
    
    // 3 months ending 2015-06-30
    re := regexp.MustCompile(`([0-9]+) months ending ([0-9]+)-([0-9]+)-([0-9]+)$`);
	matches := re.FindStringSubmatch(header);
    if (len(matches) == 5) {
        duration, err := strconv.Atoi(matches[1]);
        if (err != nil) { return nil, nil, err; }
        year, err := strconv.Atoi(matches[2]);
        if (err != nil) { return nil, nil, err; }
        month, err := strconv.Atoi(matches[3]);
        if (err != nil) { return nil, nil, err; }
        day, err := strconv.Atoi(matches[4]);
        if (err != nil) { return nil, nil, err; }
        endDate, err := time.Parse("2006-1-2", fmt.Sprintf("%d-%d-%d", year, month, day));
        if (err != nil) { return nil, nil, err; }
        startDate := endDate.AddDate(0, -duration, 0);
        return &startDate, &endDate, nil;
    }

    // As of 2016-06-30
    re = regexp.MustCompile(`As of ([0-9]+)-([0-9]+)-([0-9]+)$`);
    matches = re.FindStringSubmatch(header);
    if (len(matches) == 4) {
        year, err := strconv.Atoi(matches[1]);
        if (err != nil) { return nil, nil, err; }
        month, err := strconv.Atoi(matches[2]);
        if (err != nil) { return nil, nil, err; }
        day, err := strconv.Atoi(matches[3]);
        if (err != nil) { return nil, nil, err; }
        endDate, err := time.Parse("2006-1-2", fmt.Sprintf("%d-%d-%d", year, month, day));
        if (err != nil) { return nil, nil, err; }
        startDate := endDate;
        return &startDate, &endDate, nil;
    }

    return nil, nil, err;
}