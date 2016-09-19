package main

import (
    "net/http"
)

type HttpHandler interface {
    Process(w http.ResponseWriter, r *http.Request)
}