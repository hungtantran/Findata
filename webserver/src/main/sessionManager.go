package main

import (
    "encoding/json"
    "github.com/gorilla/sessions"
    "net/http"

    "fin_database"
)

type SessionManager interface {
    GetSession(r *http.Request, sessionName string) (*sessions.Session, error) ;
    SaveSession(session *sessions.Session, w http.ResponseWriter, r *http.Request) error;
    ClearSession(w http.ResponseWriter, sessionName string);
    ClearAllSession(w http.ResponseWriter);
    GetUserFromSession(w http.ResponseWriter, r *http.Request) *fin_database.User;
}

type FSSessionManager struct {
    store *sessions.CookieStore;
}

func NewFSSessionManager() *FSSessionManager {
    var fsSessionManager *FSSessionManager = new(FSSessionManager);
    fsSessionManager.store = sessions.NewCookieStore([]byte("session"));

    fsSessionManager.store.Options = &sessions.Options{
        Path:     "/",
        MaxAge:   60 * 60 * 24 * 30 /* 30 days */,
        HttpOnly: true,
    }

    return fsSessionManager;
}

func (fsSessionManager *FSSessionManager) GetSession(r *http.Request, sessionName string) (*sessions.Session, error) {
    return fsSessionManager.store.Get(r, sessionName);
}

func (fsSessionManager *FSSessionManager) SaveSession(session *sessions.Session, w http.ResponseWriter, r *http.Request) error {
    return session.Save(r, w);
}

func (fsSessionManager *FSSessionManager) ClearSession(w http.ResponseWriter, sessionName string) {
    cookie := &http.Cookie{
        Name:   sessionName,
        Value:  "",
        Path:   "/",
        MaxAge: -1,
    }
    http.SetCookie(w, cookie);
}

func (fsSessionManager *FSSessionManager) ClearAllSession(w http.ResponseWriter) {
    sessionNames := [3]string{"Username", "Fullname", "sid"};
    for _, sessionName := range sessionNames {
        fsSessionManager.ClearSession(w, sessionName);
    }
}

func (fsSessionManager *FSSessionManager) GetUserFromSession(w http.ResponseWriter, r *http.Request) *fin_database.User {
    session, _ := fsSessionManager.GetSession(r, "sid"); 
    userInf, ok := session.Values["user"];
    if (!ok) {
        fsSessionManager.ClearAllSession(w);
        return nil;
    }
    user := new(fin_database.User);
    json.Unmarshal(userInf.([]byte), user)
    if (!ok) {
        fsSessionManager.ClearAllSession(w);
        return nil;
    }
    return user;
}