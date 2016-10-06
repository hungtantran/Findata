package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
)

type StandardUserHandler struct {
    usersDatabase *UsersDatabase
    sessionManager SessionManager
    gridsDatabase *GridsDatabase
}

func NewStandardUserHandler(
        usersDatabase *UsersDatabase,
        sessionManager SessionManager,
        gridsDatabase *GridsDatabase) *StandardUserHandler {
    var userHandler *StandardUserHandler = new(StandardUserHandler);
    userHandler.usersDatabase = usersDatabase;
    userHandler.sessionManager = sessionManager;
    userHandler.gridsDatabase = gridsDatabase;
    return userHandler;
}

func (userHandler *StandardUserHandler) GetUserFromSession(r *http.Request) *User {
    session, _ := userHandler.sessionManager.GetSession(r, "sid"); 
    userInf, ok := session.Values["user"];
    if (!ok) {
        return nil;
    }
    user := new(User);
    json.Unmarshal(userInf.([]byte), user)
    if (!ok) {
        return nil;
    }
    return user;
} 

func (userHandler *StandardUserHandler) ProcessSaveGrid(w http.ResponseWriter, r *http.Request, param map[string]string) {
    saveResult := make(map[string]interface{});
    saveResult["result"] = false;
    saveResult["message"] = "Save fails.";
    
    user := userHandler.GetUserFromSession(r);
    if (user == nil) {
        http.Error(w, "Error", 400);
        return;
    }
    gridJson := param["grid"];

    saveResult["result"] = userHandler.gridsDatabase.InsertGrid("fake_name", user.Id.Int64, gridJson);
    saveResult["message"] = "Save succeeds.";
    fmt.Fprintf(w, mapToJsonString(saveResult));
}

func (userHandler *StandardUserHandler) ProcessLoadGrid(w http.ResponseWriter, r *http.Request, param map[string]string) {
    user := userHandler.GetUserFromSession(r);
    if (user == nil) {
        http.Error(w, "Error", 400);
        return;
    }

    var grid *Grid = userHandler.gridsDatabase.GetGrid(user.Id.Int64);
    gridJsonString := "[]";
    if (grid != nil) {
        gridJson, _ := json.Marshal(grid.Grid.String);
        gridJsonString = string(gridJson);
    }
    fmt.Fprintf(w, gridJsonString);
}

func (userHandler *StandardUserHandler) ProcessPost(w http.ResponseWriter, r *http.Request) {
    var param map[string]string;
    err := json.NewDecoder(r.Body).Decode(&param)
    if err != nil {
        http.Error(w, "Error", 400);
        return;
    }

    action, ok := param["action"];
    if (!ok) {
        http.Error(w, "Error", 400);
        return;
    }

    switch action {
    case "SaveGrid":
        userHandler.ProcessSaveGrid(w, r, param);
        return;
    case "LoadGrid":
        userHandler.ProcessLoadGrid(w, r, param);
        return;
    default:
        log.Printf("Receive non-existing search action %s", action);
        http.Error(w, "Error", 400);
        return;
    }
}

func (userHandler *StandardUserHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        page, _ := loadPage("404");
        fmt.Fprintf(w, page);
    case "POST":
        userHandler.ProcessPost(w, r);
    default:
        page, _ := loadPage("404");
        fmt.Fprintf(w, page);
    }
}