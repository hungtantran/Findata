package main

import (
	"fmt"
	elastic "gopkg.in/olivere/elastic.v3"

	"fin_database"
)

func PopulateEconomicsInfo() {
	// Create a client
	client := GetElasticSearchClient();
	var mysqlConnector *fin_database.MySqlConnector = fin_database.NewMySqlConnector(
		mysqlUsername,
		mysqlPassword,
		mysqlServer,
		mysqlDatabase);
	var economicsInfoDatabase *fin_database.EconomicsInfoDatabase = fin_database.NewEconomicsInfoDatabase(
		dbType, "economics_info", mysqlConnector);
    allEconomicsInfo := economicsInfoDatabase.GetAllEconomicsInfo();

	bulkRequest := client.Bulk();
	for _, economicsInfo := range(allEconomicsInfo) {
		economicsInfoElastic := EconomicsInfoElastic {
			Id: defaultNullInt(economicsInfo.Id),
			Name: defaultNullString(economicsInfo.Name),
			Location: defaultNullString(economicsInfo.Location),
			Category: defaultNullString(economicsInfo.Category),
			TypeStr: defaultNullString(economicsInfo.TypeStr),
			Source: defaultNullString(economicsInfo.Source),
			Metadata: defaultNullString(economicsInfo.Metadata),
		}
		indexReq := elastic.NewBulkIndexRequest().Index("findata").Type("economics_info").Id(string(economicsInfo.Id.Int64)).Doc(economicsInfoElastic)
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
	client := GetElasticSearchClient();
	var mysqlConnector *fin_database.MySqlConnector = fin_database.NewMySqlConnector(
		mysqlUsername,
		mysqlPassword,
		mysqlServer,
		mysqlDatabase);
	var tickerInfoDatabase *fin_database.TickerInfoDatabase = fin_database.NewTickerInfoDatabase(
		dbType, "ticker_info", mysqlConnector);
    allTickerInfo := tickerInfoDatabase.GetAllTickerInfo();

	bulkRequest := client.Bulk();
	for _, tickerInfo := range(allTickerInfo) {
		tickerElastic := TickerInfoElastic {
			Id: defaultNullInt(tickerInfo.Id),
			Ticker: defaultNullString(tickerInfo.Ticker),
			Ticker_type: defaultNullString(tickerInfo.TickerType),
			Name: defaultNullString(tickerInfo.Name),
			Location: defaultNullString(tickerInfo.Location),
			Cik: defaultNullString(tickerInfo.Cik),
			Ipo_year: defaultNullInt(tickerInfo.IpoYear),
			Sector: defaultNullString(tickerInfo.Sector),
			Industry: defaultNullString(tickerInfo.Industry),
			Exchange: defaultNullString(tickerInfo.Exchange),
			Sic: defaultNullInt(tickerInfo.Sic),
			Naics: defaultNullInt(tickerInfo.Naics),
			Class_share: defaultNullString(tickerInfo.ClassShare),
			Fund_type: defaultNullString(tickerInfo.FundType),
			Fund_family: defaultNullString(tickerInfo.FundFamily),
			Asset_class: defaultNullString(tickerInfo.AssetClass),
			Active: defaultNullInt(tickerInfo.Active),
			Metadata: defaultNullString(tickerInfo.MetaData),
		}
		indexReq := elastic.NewBulkIndexRequest().Index("findata").Type("ticker_info").Id(string(tickerInfo.Id.Int64)).Doc(tickerElastic)
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
	client := GetElasticSearchClient();
	var mysqlConnector *fin_database.MySqlConnector = fin_database.NewMySqlConnector(
		mysqlUsername,
		mysqlPassword,
		mysqlServer,
		mysqlDatabase);
	var exchangeIndexInfoDatabase *fin_database.ExchangeIndexInfoDatabase = fin_database.NewExchangeIndexInfoDatabase(
		dbType, "exchange_index_info", mysqlConnector);
    allExchangeIndexInfo := exchangeIndexInfoDatabase.GetAllExchangeIndexInfo();

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
	fmt.Println(bulkRequest);

	bulkResponse, err := bulkRequest.Do();
	if err != nil {
		// Handle error
		panic(err)
	}

	indexed := bulkResponse.Indexed();
	fmt.Println("Index response", len(indexed));
}