package utilities

import (
	"fmt"
    "log"
	elastic "gopkg.in/olivere/elastic.v3"

	"fin_database"
)

func PopulateNewsInfo() {
	// Create a client
	client := GetElasticSearchClient();
	var mysqlConnector *fin_database.MySqlConnector = fin_database.NewMySqlConnector(
		MysqlUsername,
		MysqlPassword,
		MysqlServer,
		MysqlDatabase);
	var newsInfoDatabase *fin_database.NewsInfoDatabase = fin_database.NewNewsInfoDatabase(
		DbType, "news_info", mysqlConnector);

	maxNumResults := 2000;
	curId := 0;

	for {
		newsInfos := newsInfoDatabase.GetNewsInfo(curId, maxNumResults);
		if len(newsInfos) == 0 {
			log.Printf("Done at curId %d", curId);
			break;
		}
		curId += maxNumResults;

		bulkRequest := client.Bulk();
		for _, newsInfo := range(newsInfos) {
			newsInfoElastic := NewsInfoElastic {
				Id: defaultNullInt(newsInfo.Id),
				Source: defaultNullString(newsInfo.Source),
				Date: defaultDate(newsInfo.Date),
				Headline: defaultNullString(newsInfo.Headline),
				PrintHeadline: defaultNullString(newsInfo.PrintHeadline),
				Abstract: defaultNullString(newsInfo.Abstract),
				Section: defaultNullString(newsInfo.Section),
				Subsection: defaultNullString(newsInfo.Subsection),
				Tags: defaultNullString(newsInfo.Tags),
				Keywords: defaultNullString(newsInfo.Keywords),
				Link: defaultNullString(newsInfo.Link),
				Authors: defaultNullString(newsInfo.Authors),
				Metadata: defaultNullString(newsInfo.Metadata),
			}
			indexReq := elastic.NewBulkIndexRequest().Index("news").Type("news_info").Id(string(newsInfo.Id.Int64)).Doc(newsInfoElastic);
			bulkRequest = bulkRequest.Add(indexReq);
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
}