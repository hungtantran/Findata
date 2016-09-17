package main

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