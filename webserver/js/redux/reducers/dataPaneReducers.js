import {FILTER_CHANGE} from '../actions/dataPaneActions';

function DataPane(state={}, action) {
    switch(action.type) {
    case FILTER_CHANGE:
        {
            let dataPane = {};
            dataPane[action.tableCode] = {};
            dataPane[action.tableCode]['filter'] = action.filter; 
            console.log(dataPane);
            return Object.assign({}, state, dataPane);
        }
    default:
        return state;
    }
}

export default DataPane;