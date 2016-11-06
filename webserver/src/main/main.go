package main

import (
    "encoding/gob"
    "log"
    "net/http"

    "fin_database"
)

var indexHandlerObj HttpHandler;
var searchHandlerObj HttpHandler;
var matchHandlerObj HttpHandler;
var userHandlerObj HttpHandler;
var signupHandlerObj HttpHandler;
var loginHandlerObj HttpHandler;
var logoutHandlerObj HttpHandler;
var contactHandlerObj HttpHandler;
var aboutHandlerObj HttpHandler;

var sessionManager SessionManager;

// Check if this is thread-safe
func getRequestUser(w http.ResponseWriter, r *http.Request) *fin_database.User {
    return sessionManager.GetUserFromSession(w, r);
}

func ProcessGeneralRequest(handlerObj HttpHandler, w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    if (handlerObj == nil) {
        http.Error(w, "Error", 400);
        return;
    }
    handlerObj.Process(w, r);
}

// TODO move database classes to their own package
func indexHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(indexHandlerObj, w, r);
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(searchHandlerObj, w, r);
}

func matchHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(matchHandlerObj, w, r);
}

func aboutHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(aboutHandlerObj, w, r);
}

func contactHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(contactHandlerObj, w, r);
}

func userHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(userHandlerObj, w, r);
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(loginHandlerObj, w, r);
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(logoutHandlerObj, w, r);
}

func signupHandler(w http.ResponseWriter, r *http.Request) {
    ProcessGeneralRequest(signupHandlerObj, w, r);
}

func initializeConfiguration() {
    // Initialize session manager
    sessionManager = NewFSSessionManager();
    gob.Register(&fin_database.User{});

    // Initialize simple handlers
    indexHandlerObj = NewStandardIndexHandler();
    contactHandlerObj = NewStandardContactHandler();
    aboutHandlerObj = NewStandardAboutHandler();

    // Initialize login, logout and register handler
    var mysqlConnector *fin_database.MySqlConnector =  fin_database.NewMySqlConnector(
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase);

    var usersDatabase *fin_database.UsersDatabase = fin_database.NewUsersDatabase(
            dbType,
            "users",
            mysqlConnector);
    var gridsDatabase *fin_database.GridsDatabase = fin_database.NewGridsDatabase(
            dbType,
            "grids",
            mysqlConnector);
    loginHandlerObj = NewStandardLoginHandler(usersDatabase);
    logoutHandlerObj = NewStandardLogoutHandler(usersDatabase);
    signupHandlerObj = NewStandardSignupHandler(usersDatabase);
    userHandlerObj = NewStandardUserHandler(usersDatabase, gridsDatabase);

    // Initialize match handler
    matchHandlerObj = NewElasticSearchMatchHandler(elasticSearchIp, elasticSearchPort);

    // Initialize search handler
    var tickerInfoDatabase *fin_database.TickerInfoDatabase = fin_database.NewTickerInfoDatabase(
            dbType,
            "ticker_info",
            mysqlConnector);
    tickerInfoChan := make(chan []fin_database.TickerInfo);
    go func() { tickerInfoChan <- tickerInfoDatabase.GetAllTickerInfo(); }();

    var economicsInfoDatabase *fin_database.EconomicsInfoDatabase = fin_database.NewEconomicsInfoDatabase(
            dbType,
            "economics_info",
            mysqlConnector);
    economicsInfoChan := make(chan []fin_database.EconomicsInfo);
    go func() { economicsInfoChan <- economicsInfoDatabase.GetAllEconomicsInfo(); }();

    var exchangeIndexInfoDatabase *fin_database.ExchangeIndexInfoDatabase = fin_database.NewExchangeIndexInfoDatabase(
            dbType,
            "exchange_index_info",
            mysqlConnector);
    exchangeIndexInfoChan := make(chan []fin_database.ExchangeIndexInfo);
    go func() { exchangeIndexInfoChan <- exchangeIndexInfoDatabase.GetAllExchangeIndexInfo(); }();

    allTickerInfo := <-tickerInfoChan;
    allEconomicsInfo := <-economicsInfoChan;
    allExchangeIndexInfo := <-exchangeIndexInfoChan;

    var metricDatabase *fin_database.MetricDatabase = fin_database.NewMetricDatabase(
            dbType, mysqlConnector);
    searchHandlerObj = NewStandardSearchHandler(
        metricDatabase,
        allTickerInfo,
        allEconomicsInfo,
        allExchangeIndexInfo,
        elasticSearchIp,
        elasticSearchPort);
}

func main() {
    // Initialize logger to output filename
    log.SetFlags(log.Lshortfile);
    // Initialize configuration constants
    var config *ProdConfig;
    config.initializeConfig();

    go initializeConfiguration();

    http.HandleFunc("/about", aboutHandler);
    http.HandleFunc("/contact", contactHandler);
    http.HandleFunc("/search", searchHandler);
    http.HandleFunc("/match", matchHandler);
    http.HandleFunc("/user", userHandler);
    http.HandleFunc("/login", loginHandler);
    http.HandleFunc("/logout", logoutHandler);
    http.HandleFunc("/signup", signupHandler);
    http.HandleFunc("/", indexHandler);
    http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("static/css/"))));
    http.Handle("/generated/", http.StripPrefix("/generated/", http.FileServer(http.Dir("static/generated/"))));

    log.Println("Start listen and serve from ", httpAddressAndPort);
    http.ListenAndServe(httpAddressAndPort, nil);
}
