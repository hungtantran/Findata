package main

type MatchResult struct {
    Abbrv string 
    Name string
    Metadata map[string]interface{}
}

type DataSet struct {
    Title string
    Type string
    Data []ResultMetric
}

type Plot struct {
    Title string
    DataSets map[string]DataSet
}

type Graph struct {
    Title string
    Plots map[string]Plot
}