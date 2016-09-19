package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
)

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
        session, _ := loginHandler.sessionManager.GetSession(r, "sid");
        session.Values["user"] = user;
        err = loginHandler.sessionManager.SaveSession(session, w, r);
        if err != nil {
            log.Println(err);
        }

        // Set extra cookie
        cookie := http.Cookie{Name: "Username", Value: user.Username.String};
        http.SetCookie(w, &cookie);
        cookie = http.Cookie{Name: "Fullname", Value: user.Fullname.String};
        http.SetCookie(w, &cookie);
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