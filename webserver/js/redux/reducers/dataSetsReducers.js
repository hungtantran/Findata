import {RECEIVE_SEARCH} from '../actions/searchBarActions';
import {REQUEST_DATA_SET, RECIEVE_DATA_SET} from '../actions/dataSetActions';

function DataSets(state={}, action) {
    switch(action.type) {
    case RECEIVE_SEARCH:
        {
            let dataSets = {};
            Object.keys(action.results).forEach((key) => {
                let pairs = action.results[key];
                pairs.forEach((pair) => {
                    dataSets[pair.id] = {name: pair.name, tableName: key, isFetching: false, data: []};
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
            let dataSetInfo = Object.assign({}, state[action.id], {isFetching: false, data: action.data});
            return Object.assign({}, state, {[action.id]: dataSetInfo});
        }
    default:
        return state;
    }
}

export default DataSets;