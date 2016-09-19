package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
)

type StandardSignupHandler struct {
    usersDatabase *UsersDatabase
}

func NewStandardSignupHandler(usersDatabase *UsersDatabase) *StandardSignupHandler {
    var signupHandler *StandardSignupHandler = new(StandardSignupHandler);
    signupHandler.usersDatabase = usersDatabase;
    return signupHandler;
}

func (signupHandler *StandardSignupHandler) ProcessPost(w http.ResponseWriter, r *http.Request) {
    registerResult := make(map[string]interface{});
    registerResult["result"] = false;
    registerResult["message"] = "Registeration fails.";

    var param map[string]string;
    err := json.NewDecoder(r.Body).Decode(&param);
    if err != nil {
        fmt.Fprintf(w, mapToJsonString(registerResult));
        return;
    }

    fullname := param["fullname"];
    email := param["email"];
    username := param["username"];
    password := param["password"];

    // TODO a lot of validation of user inputs here
    log.Println(fullname, email, username, password);
    result := signupHandler.usersDatabase.InsertUser(username, fullname, email, password);
    registerResult["result"] = result;
    if (result) {
        registerResult["message"] = "Registeration succeeds.";
    }

    fmt.Fprintf(w, mapToJsonString(registerResult))
}

func (signupHandler *StandardSignupHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        // Serve the resource.
        page, err := loadPage("signup")
        if err != nil {
            log.Println(err);
            page, err = loadPage("404")
        }
        fmt.Fprintf(w, page)
    case "POST":
        signupHandler.ProcessPost(w, r);
    default:
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    }
}