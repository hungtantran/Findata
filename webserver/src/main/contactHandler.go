package main

import (
    "fmt"
    "log"
    "net/http"
)

type StandardContactHandler struct {
}

func NewStandardContactHandler() *StandardContactHandler {
    var contactHandler *StandardContactHandler = new(StandardContactHandler);
    return contactHandler;
}

func (contactHandler *StandardContactHandler) ProcessGet(w http.ResponseWriter, r *http.Request) {
    page, err := loadPage("contact");
    if err != nil {
        log.Println(err);
        page, err = loadPage("404");
    }
    fmt.Fprintf(w, page);
}

func (contactHandler *StandardContactHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        contactHandler.ProcessGet(w, r);
    case "POST":
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    default:
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    }
}