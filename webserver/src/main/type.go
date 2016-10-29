package main

// Match type
type MatchResult struct {
    Abbrv string 
    Name string
    Metadata map[string]interface{}
}

// Metric type
type MetricType int

const (
    Indices MetricType = iota
    Equities MetricType = iota
    EconIndicator MetricType = iota
)

func (t MetricType) String() string {
    switch t {
    case Indices:
        return "Indices";
    case Equities:
        return "Equities";
    case EconIndicator:
        return "Economics Indicators";
    }
    return "";
}

// Graph type
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