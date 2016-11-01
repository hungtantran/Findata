import {RECEIVE_SEARCH} from '../actions/searchBarActions';

function DataSets(state={}, action) {
    switch(action.type) {
    case RECEIVE_SEARCH:
        {
            let dataSets = {};
            Object.keys(action.results).forEach((key) => {
                let pairs = action.results[key];
                pairs.forEach((pair) => {
                    dataSets[pair.id] = {name: pair.name, tableName: key};
                });
            });
            return Object.assign({}, state, dataSets);
        }
    default:
        return state;
    }
}

export default DataSets;