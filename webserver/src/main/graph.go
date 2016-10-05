package main

type MatchResult struct {
    Abbrv string 
    Name string
    Metadata map[string]interface{}
}

type DataSet struct {
    Title string
    Type string
    // This is a metadata that tells the server what data to fetch
    DataDesc map[string]string
}

type Plot struct {
    Title string
    DataSets map[string]DataSet
}

type Graph struct {
    Title string
    Plots map[string]Plot
}