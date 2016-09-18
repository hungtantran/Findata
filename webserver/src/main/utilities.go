package main

import (
    "io/ioutil"
    "os"
    "encoding/json"
    "log"
)

func loadPage(title string) (string, error) {
    filename :=  "templates" + string(os.PathSeparator) + title + ".html"
    body, err := ioutil.ReadFile(filename)
    if err != nil {
        return "", err
    }
    return string(body), err
}

func mapToJsonString(m map[string]interface{}) string {
    jsonString := "";
    jsonObj, err := json.Marshal(m);
    if err != nil {
        log.Println("error:", err)
    } else {
        jsonString = string(jsonObj);
    }
    return jsonString;
}