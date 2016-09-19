package main

import (
    "fmt"
    "log"
    "net/http"
)

type StandardAboutHandler struct {
}

func NewStandardAboutHandler() *StandardAboutHandler {
    var aboutHandler *StandardAboutHandler = new(StandardAboutHandler);
    return aboutHandler;
}

func (aboutHandler *StandardAboutHandler) ProcessGet(w http.ResponseWriter, r *http.Request) {
    page, err := loadPage("about");
    if err != nil {
        log.Println(err);
        page, err = loadPage("404");
    }
    fmt.Fprintf(w, page);
}

func (aboutHandler *StandardAboutHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        aboutHandler.ProcessGet(w, r);
    case "POST":
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    default:
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    }
}