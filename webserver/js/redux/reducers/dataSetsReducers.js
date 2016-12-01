import {RECEIVE_SEARCH} from '../actions/searchBarActions';
import {REQUEST_DATA_SET, RECIEVE_DATA_SET} from '../actions/dataSetActions';
import {LOAD_DATASETS} from '../actions/dashboardTabsActions';

function DataSets(state={}, action) {
    switch(action.type) {
    case RECEIVE_SEARCH:
        {
            let dataSets = {};
            // action.results is an array of DataDesc
            // DataDesc is an object:
            // {
            //     tableName string
            //     tableCode string
            //     dataType MetricType
            //     metricDescs []MetricDesc
            // }
            //
            // type MetricDesc struct {
            //     MetricName string
            //     MetricCode string
            //     id guid
            // }
            action.results.forEach((dataDesc) => {
                let tableName = dataDesc.tableName;
                let tableCode = dataDesc.tableCode;
                let dataType = dataDesc.dataType;
                let metricDescs = dataDesc.metricDescs;
                
                metricDescs.forEach((metricDesc) => {
                    dataSets[metricDesc.id] = {
                        tableName: tableName,
                        tableCode: tableCode,
                        metricName: metricDesc.MetricName,
                        metricCode: metricDesc.MetricCode,
                        isFetching: false,
                        data: [],
                        domain: [],
                        range: []};
                });
            });
            return Object.assign({}, state, dataSets);
        }
    case REQUEST_DATA_SET:
        {
            let dataSetInfo = Object.assign({}, state[action.id], {isFetching: true});
            return Object.assign({}, state, {[action.id]: dataSetInfo});
        }
    case RECIEVE_DATA_SET:
        {
            Date.MIN_VALUE = new Date(-8640000000000000);
            Date.MAX_VALUE = new Date(8640000000000000);
            let xMin = Date.MAX_VALUE, yMin = Infinity;
            let xMax = Date.MIN_VALUE, yMax = -Infinity;
            let newData = action.data.map((pair) => {
                if(pair.V < yMin)
                    yMin = pair.V;
                if(pair.V > yMax)
                    yMax = pair.V;

                let date = new Date(pair.T);

                if(date < xMin)
                    xMin = date;
                if(date > xMax)
                    xMax = date;

                return {t: date, v:pair.V};
            });

            let dataSetInfo = Object.assign(
                {},
                state[action.id],
                {isFetching: false, data: newData, range: [yMin, yMax], domain: [xMin, xMax]});
            return Object.assign({}, state, {[action.id]: dataSetInfo});
        }
    case LOAD_DATASETS:
        return Object.assign({}, action.dataSets);
    default:
        return state;
    }
}

export default DataSets;