package main

import (
    "encoding/gob"
    "log"
    "net/http"
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
func getRequestUser(w http.ResponseWriter, r *http.Request) *User {
    return sessionManager.GetUserFromSession(w, r);
}

// TODO move database classes to their own package
func indexHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    indexHandlerObj.Process(w, r);
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    searchHandlerObj.Process(w, r);
}

func matchHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    matchHandlerObj.Process(w, r);
}

func aboutHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    aboutHandlerObj.Process(w, r);
}

func contactHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    contactHandlerObj.Process(w, r);
}

func userHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    userHandlerObj.Process(w, r);
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    loginHandlerObj.Process(w, r);
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    logoutHandlerObj.Process(w, r);
}

func signupHandler(w http.ResponseWriter, r *http.Request) {
    getRequestUser(w, r);
    signupHandlerObj.Process(w, r);
}

func initializeConfiguration() {
    // Initialize session manager
    sessionManager = NewFSSessionManager();
    gob.Register(&User{});

    // Initialize simple handlers
    indexHandlerObj = NewStandardIndexHandler();
    contactHandlerObj = NewStandardContactHandler();
    aboutHandlerObj = NewStandardAboutHandler();

    // Initialize login, logout and register handler
    var usersDatabase *UsersDatabase = NewUsersDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "");
    var gridsDatabase *GridsDatabase = NewGridsDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "");
    loginHandlerObj = NewStandardLoginHandler(usersDatabase);
    logoutHandlerObj = NewStandardLogoutHandler(usersDatabase);
    signupHandlerObj = NewStandardSignupHandler(usersDatabase);
    userHandlerObj = NewStandardUserHandler(usersDatabase, gridsDatabase);
    
    // Initialize search handler
    var metricDatabase *MetricDatabase = NewMetricDatabase(
            dbType,
            mysqlUsername,
            mysqlPassword,
            mysqlServer,
            mysqlDatabase,
            "");
    searchHandlerObj = NewStandardSearchHandler(metricDatabase);

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
