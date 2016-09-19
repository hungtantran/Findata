package main

import (
    "fmt"
    "log"
    "net/http"
)

type StandardIndexHandler struct {
}

func NewStandardIndexHandler() *StandardIndexHandler {
    var indexHandler *StandardIndexHandler = new(StandardIndexHandler);
    return indexHandler;
}

func (indexHandler *StandardIndexHandler) ProcessGet(w http.ResponseWriter, r *http.Request) {
    page, err := loadPage("Index");
    if err != nil {
        log.Println(err);
        page, err = loadPage("404");
    }
    fmt.Fprintf(w, page);
}

func (indexHandler *StandardIndexHandler) Process(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        indexHandler.ProcessGet(w, r);
    case "POST":
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    default:
        page, _ := loadPage("404")
        fmt.Fprintf(w, page)
    }
}