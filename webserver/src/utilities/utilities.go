package utilities

import (
	"database/sql"
	"fmt"
	"time"
	"os"
	"log"
	elastic "gopkg.in/olivere/elastic.v3"

	"fin_database"
)

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

func defaultDate(date time.Time) string {
	year := date.Year();
	month := date.Month();
	day := date.Day();
	//hour := date.Hour();
	//minute := date.Minute();
	//second := date.Second();

	//str := 	fmt.Sprintf("%04d-%02d-%02d %02d:%02d:%02d", year, month, day, hour, minute, second);
	str := 	fmt.Sprintf("%04d-%02d-%02d", year, month, day);
	return str;
}

func GetElasticSearchClient() *elastic.Client {
	var connectionString string = ElasticSearchIp + ":" + fmt.Sprintf("%d", ElasticSearchPort);
	client, err := elastic.NewClient(
        elastic.SetURL(connectionString),
        elastic.SetSniff(false),
        elastic.SetHealthcheckInterval(10*time.Second),
        elastic.SetMaxRetries(5),
        elastic.SetErrorLog(log.New(os.Stderr, "ELASTIC ", log.LstdFlags)),
        elastic.SetInfoLog(log.New(os.Stdout, "", log.LstdFlags)))
	if err != nil {
		// Handle error
		panic(err)
	}
	return client;
}

func GetDefaultMysqlConnector() *fin_database.MySqlConnector {
	var mysqlConnector *fin_database.MySqlConnector = fin_database.NewMySqlConnector(
		MysqlUsername,
		MysqlPassword,
		MysqlServer,
		MysqlDatabase);
	return mysqlConnector;
}
