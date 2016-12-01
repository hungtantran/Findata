import {RECEIVE_SEARCH} from '../actions/searchBarActions';
import {LOAD_INSTRUMENTS} from '../actions/dashboardTabsActions';

function Instruments(state={}, action) {
    switch(action.type) {
    case RECEIVE_SEARCH:
        {
            let instruments = {};
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
                if (state[dataDesc.tableCode]) {
                    instruments[dataDesc.tableCode] = Object.assign({}, state[dataDesc.tableCode]);
                } else {
                    instruments[dataDesc.tableCode] = {};
                }

                let metricDescs = dataDesc.metricDescs;
                metricDescs.forEach((metricDesc) => {
                    instruments[dataDesc.tableCode][metricDesc.MetricCode] = metricDesc.id;
                });
            });
            return Object.assign({}, state, instruments);
        }
    case LOAD_INSTRUMENTS:
        return Object.assign({}, action.instruments);
    default:
        return state;
    }
}

export default Instruments;