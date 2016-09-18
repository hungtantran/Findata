package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
)

type LoginHandler interface {
    Process(w http.ResponseWriter, r *http.Request) 
}

type StandardLoginHandler struct {
    usersDatabase *UsersDatabase
    sessionManager SessionManager
}

func NewStandardLoginHandler(usersDatabase *UsersDatabase, sessionManager SessionManager) *StandardLoginHandler {
    var loginHandler *StandardLoginHandler = new(StandardLoginHandler);
    loginHandler.usersDatabase = usersDatabase;
    loginHandler.sessionManager = sessionManager;
    return loginHandler;
}

func (loginHandler *StandardLoginHandler) ProcessPost(w http.ResponseWriter, r *http.Request) {
    loginResult := make(map[string]interface{});
    loginResult["result"] = false;
    loginResult["message"] = "Login fails.";

    var param map[string]string;
    err := json.NewDecoder(r.Body).Decode(&param);
    if err != nil {
        fmt.Fprintf(w, mapToJsonString(loginResult));
        return;
    }

    username := param["username"];
    password := param["password"];

    // TODO a lot of validation of user inputs here
    log.Println(username, password);
    user := loginHandler.usersDatabase.GetUser(username, password);
    if (user != nil) {
        loginResult["result"] = true;
        loginResult["message"] = "Login succeeds.";
        cookies := r.Cookies();
        log.Println(cookies);
        session, _ := loginHandler.sessionManager.GetSession(r);
        log.Println(session.Values);
        session.Values["user"] = "haha" + user.Fullname.String;
        log.Println(session.Values);
        err = loginHandler.sessionManager.SaveSession(session, w, r);
        log.Println(err);

        session2, _ := loginHandler.sessionManager.GetSession(r);
        log.Println(session2.Values);
        log.Println("Done");
    }

    fmt.Fprintf(w, mapToJsonString(loginResult))
}

func (loginHandler *StandardLoginHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        // Serve the resource.
        page, err := loadPage("login")
        if err != nil {
            log.Println(err);
            page, err = loadPage("404")
        }
        fmt.Fprintf(w, page)
    case "POST":
        loginHandler.ProcessPost(w, r);
    default:
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    }
}