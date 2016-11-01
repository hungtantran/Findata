import {RECEIVE_SEARCH} from '../actions/searchBarActions';

function Instruments(state={}, action) {
    switch(action.type) {
    case RECEIVE_SEARCH:
        {
            let instruments = {};
            Object.keys(action.results).forEach((key) => {
                let pairs = action.results[key];
                instruments[key] = [];
                pairs.forEach((pair) => {
                    instruments[key].push(pair.id);
                });
            });
            return Object.assign({}, state, instruments);
        }
    default:
        return state;
    }
}

export default Instruments;