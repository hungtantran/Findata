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
    query := "SELECT * FROM " + tableName + " WHERE metric_name = '" + metricName + "' ORDER BY end_date";
    if metricName == "" {
        query = "SELECT * FROM " + tableName + " ORDER BY end_date";
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
    var startDate time.Time;
    for rows.Next() {
        err := rows.Scan(
                &id,
                &name,
                &metric.V,
                &unit,
                &startDate,
                &metric.T,
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

func (metricDatabase *MetricDatabase) InsertMetric(tableName string, metric *Metric) int64 {
    stmt, err := metricDatabase.dbConnector.GetConnector().Prepare(
            "INSERT " + tableName + " SET id=?, metric_name=?, value=?, unit=?, start_date=?, end_date=?, metadata=? ON DUPLICATE KEY UPDATE value=?, unit=?, metadata=?");
    defer stmt.Close();
    if err != nil {
        log.Println(err);
        return -1;
    }

    res, err := stmt.Exec(
            metric.Id,
            metric.MetricName,
            metric.Value,
            metric.Unit,
            metric.StartDate,
            metric.EndDate,
            metric.MetaData,
            metric.Value,
            metric.Unit,
            metric.MetaData);
    if err != nil {
        log.Println(err);
        return -1;
    }

    lastId, err := res.LastInsertId();
    if err != nil {
        log.Println(err);
        return -1;
    }

    return lastId;
}

func (metricDatabase *MetricDatabase) GetAllDimensions(tableName string) map[string]TickerInfoDimension {
    rows, err := metricDatabase.dbConnector.GetConnector().Query(
        "SELECT metric_name, metric_name, count(*) as count from " + tableName + " group by metric_name having count > 1");
    if err != nil {
        log.Println(err)
    }
    defer rows.Close()
    var metricDimension TickerInfoDimension;
    allMetricsDimensions := make(map[string]TickerInfoDimension);
    for rows.Next() {
        var count int;
        err := rows.Scan(
                &metricDimension.Abbrv,
                &metricDimension.Name,
                &count);
        if err != nil {
            log.Println(err);
        }
        allMetricsDimensions[metricDimension.Abbrv.String] = metricDimension;
    }
    err = rows.Err()
    if err != nil {
        log.Println(err);
    }
    log.Println("Found", len(allMetricsDimensions), "metric dimensions");
    return allMetricsDimensions;
}

func (metricDatabase *MetricDatabase) Close() {
    metricDatabase.dbConnector.Close();
}