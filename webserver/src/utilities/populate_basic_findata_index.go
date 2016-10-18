package main

import (
	"fmt"
    "time"
    "log"
    "os"
	"database/sql"
	elastic "gopkg.in/olivere/elastic.v3"
)

type TickerInfoElastic struct {
    Id int64 `json:"id"`
    Ticker string `json:"ticker"`
    Ticker_type string `json:"ticker_type"`
    Name string `json:"name"`
    Location string `json:"location"`
    Cik string `json:"cik"`
    Ipo_year int64 `json:"ipo_year"`
    Sector string `json:"sector"`
    Industry string `json:"industry"`
    Exchange string `json:"exchange"`
    Sic int64 `json:"sic"`
    Naics int64 `json:"naics"`
    Class_share string `json:"class_share"`
    Fund_type string `json:"fund_type"`
    Fund_family string `json:"fund_family"`
    Asset_class string `json:"asset_class"`
    Active int64 `json:"active"`
    Metadata string `json:"metadata"`
}

type ExchangeIndexInfoElastic struct {
    Id int64 `json:"id"`
    Index string `json:"index"`
    IndexType string `json:"index_type"`
    Name string `json:"name"`
    Location string `json:"location"`
    Sector string `json:"sector"`
    Industry string `json:"industry"`
    Metadata string `json:"metadata"`
}

type EconomicsInfoElastic struct {
    Id int64 `json:"id"`
    Name string `json:"name"`
    Location string `json:"location"`
    Category string `json:"category"`
    TypeStr string `json:"type"`
    Source string `json:"source"`
    Metadata string `json:"metadata"`
}

func defaultNullInt(val sql.NullInt64) int64 {
	if val.Valid {
		return val.Int64;
	}

	return 0;
}

func defaultNullString(val sql.NullString) string {
	if val.Valid {
		return val.String;
	}

	return "";
}

func PopulateEconomicsInfo() {
	// Create a client
	client, err := elastic.NewClient(
        elastic.SetURL("104.198.15.187:9200"),
        elastic.SetSniff(false),
        elastic.SetHealthcheckInterval(10*time.Second),
        elastic.SetMaxRetries(5),
        elastic.SetErrorLog(log.New(os.Stderr, "ELASTIC ", log.LstdFlags)),
        elastic.SetInfoLog(log.New(os.Stdout, "", log.LstdFlags)))
	if err != nil {
		// Handle error
		panic(err)
	}

	var economicsInfoDatabase *EconomicsInfoDatabase = NewEconomicsInfoDatabase(
		dbType,
		mysqlUsername,
		mysqlPassword,
		mysqlServer,
		mysqlDatabase,
		"");
    allEconomicsInfo := economicsInfoDatabase.getAllEconomicsInfo();

	bulkRequest := client.Bulk();
	for _, economicsInfo := range(allEconomicsInfo) {
		economicsInfoElastic := EconomicsInfoElastic {
			Id: defaultNullInt(economicsInfo.id),
			Name: defaultNullString(economicsInfo.name),
			Location: defaultNullString(economicsInfo.location),
			Category: defaultNullString(economicsInfo.category),
			TypeStr: defaultNullString(economicsInfo.typeStr),
			Source: defaultNullString(economicsInfo.source),
			Metadata: defaultNullString(economicsInfo.metadata),
		}
		indexReq := elastic.NewBulkIndexRequest().Index("findata").Type("economics_info").Id(string(economicsInfo.id.Int64)).Doc(economicsInfoElastic)
		bulkRequest = bulkRequest.Add(indexReq)
	}

	fmt.Println("Num bulk request", bulkRequest.NumberOfActions());

	bulkResponse, err := bulkRequest.Do();
	if err != nil {
		// Handle error
		panic(err)
	}

	indexed := bulkResponse.Indexed();
	fmt.Println("Index response", len(indexed));
}

func PopulateTickerInfo() {
	// Create a client
	client, err := elastic.NewClient(
        elastic.SetURL("104.198.15.187:9200"),
        elastic.SetSniff(false),
        elastic.SetHealthcheckInterval(10*time.Second),
        elastic.SetMaxRetries(5),
        elastic.SetErrorLog(log.New(os.Stderr, "ELASTIC ", log.LstdFlags)),
        elastic.SetInfoLog(log.New(os.Stdout, "", log.LstdFlags)))
	if err != nil {
		// Handle error
		panic(err)
	}

	var tickerInfoDatabase *TickerInfoDatabase = NewTickerInfoDatabase(
		dbType,
		mysqlUsername,
		mysqlPassword,
		mysqlServer,
		mysqlDatabase,
		"");
    allTickerInfo := tickerInfoDatabase.getAllTickerInfo();

	bulkRequest := client.Bulk();
	for _, tickerInfo := range(allTickerInfo) {
		tickerElastic := TickerInfoElastic {
			Id: defaultNullInt(tickerInfo.id),
			Ticker: defaultNullString(tickerInfo.ticker),
			Ticker_type: defaultNullString(tickerInfo.tickerType),
			Name: defaultNullString(tickerInfo.name),
			Location: defaultNullString(tickerInfo.location),
			Cik: defaultNullString(tickerInfo.cik),
			Ipo_year: defaultNullInt(tickerInfo.ipoYear),
			Sector: defaultNullString(tickerInfo.sector),
			Industry: defaultNullString(tickerInfo.industry),
			Exchange: defaultNullString(tickerInfo.exchange),
			Sic: defaultNullInt(tickerInfo.sic),
			Naics: defaultNullInt(tickerInfo.naics),
			Class_share: defaultNullString(tickerInfo.classShare),
			Fund_type: defaultNullString(tickerInfo.fundType),
			Fund_family: defaultNullString(tickerInfo.fundFamily),
			Asset_class: defaultNullString(tickerInfo.assetClass),
			Active: defaultNullInt(tickerInfo.active),
			Metadata: defaultNullString(tickerInfo.metaData),
		}
		indexReq := elastic.NewBulkIndexRequest().Index("findata").Type("ticker_info").Id(string(tickerInfo.id.Int64)).Doc(tickerElastic)
		bulkRequest = bulkRequest.Add(indexReq)
	}

	fmt.Println("Num bulk request", bulkRequest.NumberOfActions());

	bulkResponse, err := bulkRequest.Do();
	if err != nil {
		// Handle error
		panic(err)
	}

	indexed := bulkResponse.Indexed();
	fmt.Println("Index response", len(indexed));
}

func PopulateExchangeIndexInfo() {
	// Create a client
	client, err := elastic.NewClient(
        elastic.SetURL("104.198.15.187:9200"),
        elastic.SetSniff(false),
        elastic.SetHealthcheckInterval(10*time.Second),
        elastic.SetMaxRetries(5),
        elastic.SetErrorLog(log.New(os.Stderr, "ELASTIC ", log.LstdFlags)),
        elastic.SetInfoLog(log.New(os.Stdout, "", log.LstdFlags)))
	if err != nil {
		// Handle error
		panic(err)
	}

	var exchangeIndexInfoDatabase *ExchangeIndexInfoDatabase = NewExchangeIndexInfoDatabase(
		dbType,
		mysqlUsername,
		mysqlPassword,
		mysqlServer,
		mysqlDatabase,
		"");
    allExchangeIndexInfo := exchangeIndexInfoDatabase.getAllExchangeIndexInfo();

	bulkRequest := client.Bulk();
	for _, exchangeIndexInfo := range(allExchangeIndexInfo) {
		exchangeIndexInfoElastic := ExchangeIndexInfoElastic {
			Id: defaultNullInt(exchangeIndexInfo.Id),
			Index: defaultNullString(exchangeIndexInfo.Index),
			IndexType: defaultNullString(exchangeIndexInfo.IndexType),
			Name: defaultNullString(exchangeIndexInfo.Name),
			Location: defaultNullString(exchangeIndexInfo.Location),
			Sector: defaultNullString(exchangeIndexInfo.Sector),
			Industry: defaultNullString(exchangeIndexInfo.Industry),
			Metadata: defaultNullString(exchangeIndexInfo.Metadata),
		}
		indexReq := elastic.NewBulkIndexRequest().Index("findata").Type("exchange_index_info").Id(string(exchangeIndexInfo.Id.Int64)).Doc(exchangeIndexInfoElastic)
		fmt.Println("indexReq", indexReq);
		bulkRequest = bulkRequest.Add(indexReq)
	}

	fmt.Println("Num bulk request", bulkRequest.NumberOfActions());

	bulkResponse, err := bulkRequest.Do();
	if err != nil {
		// Handle error
		panic(err)
	}

	indexed := bulkResponse.Indexed();
	fmt.Println("Index response", len(indexed));
}