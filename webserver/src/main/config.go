package main

var dbType string

var mysqlUsername string;
var mysqlPassword string;
var mysqlServer string;
var mysqlDatabase string;

var maxNumMatchesReturned int

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
}