package main

import (
    "github.com/gorilla/sessions"
    "net/http"
)

type SessionManager interface {
    GetSession(r *http.Request, sessionName string) (*sessions.Session, error) ;
    SaveSession(session *sessions.Session, w http.ResponseWriter, r *http.Request) error;
    ClearSession(w http.ResponseWriter, sessionName string);
}

type FSSessionManager struct {
    store *sessions.CookieStore;
}

func NewFSSessionManager() *FSSessionManager {
    var fsSessionManager *FSSessionManager = new(FSSessionManager);
    fsSessionManager.store = sessions.NewCookieStore([]byte("session"));

    fsSessionManager.store.Options = &sessions.Options{
        Path:     "/",
        MaxAge:   3600,
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