package main

import (
    "github.com/gorilla/sessions"
    "net/http"
)


type SessionManager interface {
    GetSession(r *http.Request) (*sessions.Session, error) ;
    SaveSession(session *sessions.Session, w http.ResponseWriter, r *http.Request) error;
}

type FSSessionManager struct {
    store *sessions.CookieStore;
}

func NewFSSessionManager() *FSSessionManager {
    var fsSessionManager *FSSessionManager = new(FSSessionManager);
    fsSessionManager.store = sessions.NewCookieStore([]byte("session"));

    fsSessionManager.store.Options = &sessions.Options{
        Path:     "/",
        MaxAge:   3600 * 4,
        HttpOnly: true,
    }

    return fsSessionManager;
}

func (fsSessionManager *FSSessionManager) GetSession(r *http.Request) (*sessions.Session, error) {
    return fsSessionManager.store.Get(r, "sid");
}

func (fsSessionManager *FSSessionManager) SaveSession(session *sessions.Session, w http.ResponseWriter, r *http.Request) error {
    return session.Save(r, w);
}