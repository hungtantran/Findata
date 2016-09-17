export default function MetricTypeToString(metricType) {
    switch(metricType) {
        case "0":
            return "Indices";
        case "1":
            return "Equities";
        case "2":
            return "Economics Indicators";
        default:
            return "";
    }
}
