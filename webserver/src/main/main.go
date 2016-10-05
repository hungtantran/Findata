package main

import (
    "encoding/gob"
    "log"
    "net/http"
)

var indexHandlerObj HttpHandler;
var searchHandlerObj HttpHandler;
var matchHandlerObj HttpHandler;
var signupHandlerObj HttpHandler;
var loginHandlerObj HttpHandler;
var logoutHandlerObj HttpHandler;
var contactHandlerObj HttpHandler;
var aboutHandlerObj HttpHandler;

var metricDatabase *MetricDatabase;

var sessionManager SessionManager;

// TODO move database classes to their own package
func indexHandler(w http.ResponseWriter, r *http.Request) {
    indexHandlerObj.Process(w, r);
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
    searchHandlerObj.Process(w, r);
}

func matchHandler(w http.ResponseWriter, r *http.Request) {
    matchHandlerObj.Process(w, r);
}

func aboutHandler(w http.ResponseWriter, r *http.Request) {
    aboutHandlerObj.Process(w, r);
}

func contactHandler(w http.ResponseWriter, r *http.Request) {
    contactHandlerObj.Process(w, r);
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
    loginHandlerObj.Process(w, r);
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
    logoutHandlerObj.Process(w, r);
}

func signupHandler(w http.ResponseWriter, r *http.Request) {
    signupHandlerObj.Process(w, r);
}

func initializeConfiguration() {
    // Initialize logger to output filename
    log.SetFlags(log.Lshortfile);
    
    // Initialize configuration constants
    var config *ProdConfig;
    config.initializeConfig();

    // Initialize session manager
    sessionManager = NewFSSessionManager();
    gob.Register(&User{});

    // Initialize simple handlers
    indexHandlerObj = NewStandardIndexHandler();
    contactHandlerObj = NewStandardContactHandler();
    aboutHandlerObj = NewStandardAboutHandler();

    // Initialize match handler
    var tickerInfoDatabase *TickerInfoDatabase = NewTickerInfoDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "");
    tickerInfoChan := make(chan []TickerInfo);
    go func() { tickerInfoChan <- tickerInfoDatabase.getAllTickerInfo(); }();

    var economicsInfoDatabase *EconomicsInfoDatabase = NewEconomicsInfoDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "economics_info");
    economicsInfoChan := make(chan []EconomicsInfo);
    go func() { economicsInfoChan <- economicsInfoDatabase.getAllEconomicsInfo(); }();

    var exchangeIndexInfoDatabase *ExchangeIndexInfoDatabase = NewExchangeIndexInfoDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "");
    exchangeIndexInfoChan := make(chan []ExchangeIndexInfo);
    go func() { exchangeIndexInfoChan <- exchangeIndexInfoDatabase.getAllExchangeIndexInfo(); }();

    allTickerInfo := <-tickerInfoChan;
    allEconomicsInfo := <-economicsInfoChan;
    allExchangeIndexInfo := <-exchangeIndexInfoChan;
    matchHandlerObj = NewStandardMatchHandler(allTickerInfo, allEconomicsInfo, allExchangeIndexInfo);

    // Initialize login, logout and register handler
    var usersDatabase *UsersDatabase = NewUsersDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "");
    loginHandlerObj = NewStandardLoginHandler(usersDatabase, sessionManager);
    logoutHandlerObj = NewStandardLogoutHandler(usersDatabase, sessionManager);
    signupHandlerObj = NewStandardSignupHandler(usersDatabase);
    
    // Initialize search handler
    metricDatabase = NewMetricDatabase(dbType,
        mysqlUsername,
        mysqlPassword,
        mysqlServer,
        mysqlDatabase,
        "");
    searchHandlerObj = NewStandardSearchHandler(metricDatabase);
}

func main() {
    go initializeConfiguration();

    http.HandleFunc("/about", aboutHandler);
    http.HandleFunc("/contact", contactHandler);
    http.HandleFunc("/search", searchHandler);
    http.HandleFunc("/match", matchHandler);
    http.HandleFunc("/login", loginHandler);
    http.HandleFunc("/logout", logoutHandler);
    http.HandleFunc("/signup", signupHandler);
    http.HandleFunc("/", indexHandler);
    http.Handle("/css/", http.StripPrefix("/css/", http.FileServer(http.Dir("static/css/"))));
    http.Handle("/generated/", http.StripPrefix("/generated/", http.FileServer(http.Dir("static/generated/"))));

    log.Println("Start listen and serve from ", httpAddressAndPort);
    http.ListenAndServe(httpAddressAndPort, nil);
}
