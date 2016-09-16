package main

import (
    "database/sql"
    _ "github.com/go-sql-driver/mysql"
    "strconv"
    "log"
    "time"
)

type Metric struct {
    Id sql.NullInt64
    MetricName sql.NullString
    Value sql.NullFloat64
    Unit sql.NullString
    StartDate time.Time
    EndDate time.Time
    MetaData sql.NullString
}

func (metric *Metric) String() string {
    return  string(metric.Id.Int64) + " " +
            metric.MetricName.String + " " +
            strconv.FormatFloat(metric.Value.Float64, 'f', 6, 64) + " " +
            metric.Unit.String + " " +
            time.Time.String(metric.StartDate) + " " +
            time.Time.String(metric.EndDate) + " " +
            metric.MetaData.String;
}

type ResultMetric struct {
    V float64
    T time.Time
}

type MetricDatabase struct {
    dbType string
    dbUserName string
    dbPassword string
    dbServer string
    dbDatabase string
    dbTableName string
    db *sql.DB
}

func NewMetricDatabase(
        dbType string,
        dbUserName string, 
        dbPassword string,
        dbServer string,
        dbDatabase string,
        dbTableName string) *MetricDatabase {
    log.Println(dbType, dbUserName, dbPassword, dbServer, dbDatabase, dbTableName)
    var metricDatabase *MetricDatabase = new(MetricDatabase);
    metricDatabase.dbType = dbType;
    metricDatabase.dbUserName = dbUserName;
    metricDatabase.dbPassword = dbPassword;
    metricDatabase.dbServer = dbServer;
    metricDatabase.dbDatabase = dbDatabase;
    metricDatabase.dbTableName = dbTableName;

    connectionString :=
        metricDatabase.dbUserName + ":" +
        metricDatabase.dbPassword + "@tcp(" + 
        metricDatabase.dbServer + ":3306)/" +
        metricDatabase.dbDatabase + "?parseTime=true";
    log.Println("Connect to metric database use connection string " + connectionString);
    db, err := sql.Open(metricDatabase.dbType, connectionString)
	if err != nil {
		log.Println(err)
	}
    metricDatabase.db = db;
    return metricDatabase;
}

func (metricDatabase *MetricDatabase) getMetricWithName(tableName string, metricName string) []ResultMetric {
    // TODO sql injection
    query := "SELECT * FROM " + tableName + " WHERE metric_name = '" + metricName + "' ORDER BY start_date";
    if metricName == "" {
        query = "SELECT * FROM " + tableName + " ORDER BY start_date";
    }
    rows, err := metricDatabase.db.Query(query);
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

func (metricDatabase *MetricDatabase) close() {
    metricDatabase.db.Close();
}