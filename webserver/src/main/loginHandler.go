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

func (loginHandler *StandardLoginHandler) SaveSession(w http.ResponseWriter, r *http.Request, user *User) error {
    session, _ := loginHandler.sessionManager.GetSession(r, "sid");
    session.Values["user"], _ = json.Marshal(user);
    err := loginHandler.sessionManager.SaveSession(session, w, r);
    if err != nil {
        log.Println(err);
        return err;
    }
    // Set extra cookie
    cookie := http.Cookie{Name: "Username", Value: user.Username.String};
    http.SetCookie(w, &cookie);
    cookie = http.Cookie{Name: "Fullname", Value: user.Fullname.String};
    http.SetCookie(w, &cookie);

    return nil;
}

func (loginHandler *StandardLoginHandler) HandleGoogleLogin(w http.ResponseWriter, r *http.Request, param *map[string]string) (bool, string) {
    var result = false;
    var message = "Login fails.";

    typeStr := (*param)["type"];
    fullname := (*param)["fullname"];
    email := (*param)["email"];
    username := (*param)["username"];
    password := (*param)["password"];
    id_token := (*param)["id_token"];

    resp, err := http.Get("https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" + id_token);
    defer resp.Body.Close()
    if err == nil {
        user := loginHandler.usersDatabase.GetUser(username, password);
        // If user doesn't exist, register him 
        if user == nil {
            result := loginHandler.usersDatabase.InsertUser(typeStr, username, fullname, email, password);
            if result {
                user = loginHandler.usersDatabase.GetUserByUsername(username);
            }
        }

        if user != nil {
            err = loginHandler.SaveSession(w, r, user);
            if err != nil {
                result = true;
                message = "Login succeeds.";
            } 
        }
    }

    return result, message;
}

func (loginHandler *StandardLoginHandler) HandleFindataLogin(w http.ResponseWriter, r *http.Request, param *map[string]string) (bool, string) {
    var result = false;
    var message = "Login fails.";

    username := (*param)["username"];
    password := (*param)["password"];
    user := loginHandler.usersDatabase.GetUser(username, password);
    if (user != nil) {
        err := loginHandler.SaveSession(w, r, user);
        if err != nil {
            result = true;
            message = "Login succeeds.";
        } 
    }

    return result, message;
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

    // TODO a lot of validation of user inputs here
    loginType := param["type"];
    if (loginType == "Google") {
        loginResult["result"], loginResult["message"] = loginHandler.HandleGoogleLogin(w, r, &param);
    } else if (loginType == "Findata") {
        loginResult["result"], loginResult["message"] = loginHandler.HandleFindataLogin(w, r, &param);
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