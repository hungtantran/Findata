package main

import (
    "fmt"
    "net/http"
)

type StandardLogoutHandler struct {
    usersDatabase *UsersDatabase
}

func NewStandardLogoutHandler(usersDatabase *UsersDatabase) *StandardLogoutHandler {
    var logoutHandler *StandardLogoutHandler = new(StandardLogoutHandler);
    logoutHandler.usersDatabase = usersDatabase;
    return logoutHandler;
}

func (logoutHandler *StandardLogoutHandler) Logout(w http.ResponseWriter, r *http.Request) {
    sessionManager.ClearAllSession(w);
    http.Redirect(w, r, "/", 302);
}

func (logoutHandler *StandardLogoutHandler) ProcessGet(w http.ResponseWriter, r *http.Request) {
    logoutHandler.Logout(w, r);
}

func (logoutHandler *StandardLogoutHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        logoutHandler.ProcessGet(w, r);
    case "POST":
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    default:
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    }
}