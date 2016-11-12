package utilities

var DbType string

var MysqlUsername string;
var MysqlPassword string;
var MysqlServer string;
var MysqlDatabase string;

var ElasticSearchIp string;
var ElasticSearchPort int;

var MaxNumMatchesReturned int;

var HttpAddressAndPort string;

var OauthClientId string;
var OauthClientSecret string;

type Config interface {
    InitializeConfig()
}

type ProdConfig struct {
}

func (config *ProdConfig) InitializeConfig() {
    DbType = "mysql"

    MysqlUsername = "root";
    MysqlPassword = "testtest";
    MysqlServer = "104.154.40.63";
    MysqlDatabase = "models";

    ElasticSearchIp = "104.198.15.187";
    ElasticSearchPort = 9200;

    MaxNumMatchesReturned = 10;

    HttpAddressAndPort = "localhost:8080";
    
    OauthClientId = "292129338715-hv2qf7rlvgq00dpjn9h7q04otkoan1fh.apps.googleusercontent.com";
    OauthClientSecret = "ESk1Pw0yR-FhbCAcPgm6Z8NV";   
}