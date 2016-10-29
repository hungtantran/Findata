package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"

    "fin_database"
)

type StandardUserHandler struct {
    usersDatabase *fin_database.UsersDatabase
    gridsDatabase *fin_database.GridsDatabase
}

func NewStandardUserHandler(
        usersDatabase *fin_database.UsersDatabase,
        gridsDatabase *fin_database.GridsDatabase) *StandardUserHandler {
    var userHandler *StandardUserHandler = new(StandardUserHandler);
    userHandler.usersDatabase = usersDatabase;
    userHandler.gridsDatabase = gridsDatabase;
    return userHandler;
}

func (userHandler *StandardUserHandler) ProcessSaveGrid(w http.ResponseWriter, r *http.Request, param map[string]string) {
    saveResult := make(map[string]interface{});
    saveResult["result"] = false;
    saveResult["message"] = "Save fails.";
    
    user := sessionManager.GetUserFromSession(w, r);
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
    user := sessionManager.GetUserFromSession(w, r);
    if (user == nil) {
        http.Error(w, "Error", 400);
        return;
    }

    var grid *fin_database.Grid = userHandler.gridsDatabase.GetGrid(user.Id.Int64);
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