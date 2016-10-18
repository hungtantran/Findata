package main

var dbType string

var mysqlUsername string;
var mysqlPassword string;
var mysqlServer string;
var mysqlDatabase string;

var maxNumMatchesReturned int;

var httpAddressAndPort string;

var oauthClientId string;
var oauthClientSecret string;

type Config interface {
    initializeConfig()
}

type ProdConfig struct {
}

func (config *ProdConfig) initializeConfig() {
    dbType = "mysql"

    mysqlUsername = "root";
    mysqlPassword = "testtest";
    mysqlServer = "104.154.40.63";
    mysqlDatabase = "models";

    maxNumMatchesReturned = 10;

    httpAddressAndPort = "localhost:8080";
    
    oauthClientId = "292129338715-hv2qf7rlvgq00dpjn9h7q04otkoan1fh.apps.googleusercontent.com";
    oauthClientSecret = "ESk1Pw0yR-FhbCAcPgm6Z8NV";   
}