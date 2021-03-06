package fin_database

import (
    "database/sql"
    "log"
    "time"
)

type MetricDatabase struct {
    dbType string
    dbConnector *MySqlConnector
}

func NewMetricDatabase(
        dbType string,
        dbConnector *MySqlConnector) *MetricDatabase {
    log.Println(dbType)
    var metricDatabase *MetricDatabase = new(MetricDatabase);
    metricDatabase.dbType = dbType;
    metricDatabase.dbConnector = dbConnector;
    return metricDatabase;
}

func (metricDatabase *MetricDatabase) GetMetricWithName(tableName string, metricName string) []ResultMetric {
    // TODO sql injection
    query := "SELECT * FROM " + tableName + " WHERE metric_name = '" + metricName + "' ORDER BY start_date";
    if metricName == "" {
        query = "SELECT * FROM " + tableName + " ORDER BY start_date";
    }
    rows, err := metricDatabase.dbConnector.GetConnector().Query(query);
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var metric ResultMetric;
    var allMetric []ResultMetric;
    
    var id sql.NullInt64;
    var name, unit, metaData sql.NullString;
    var endDate time.Time;
    for rows.Next() {
        err := rows.Scan(
                &id,
                &name,
                &metric.V,
                &unit,
                &metric.T,
                &endDate,
                &metaData);
        if err != nil {
            log.Println(err);
        }
        allMetric = append(allMetric, metric);
    }
    err = rows.Err()
    if err != nil {
        log.Println(err);
    }
    return allMetric;
}

func (metricDatabase *MetricDatabase) Close() {
    metricDatabase.dbConnector.Close();
}