import {RECEIVE_SEARCH} from '../actions/searchBarActions';

function Instruments(state={}, action) {
    switch(action.type) {
    case RECEIVE_SEARCH:
        {
            let instruments = {};
            Object.keys(action.results).forEach((key) => {
                if (state[key]) {
                    instruments[key] = Object.assign({}, state[key]);
                } else {
                    instruments[key] = {};
                }

                let pairs = action.results[key];
                pairs.forEach((pair) => {
                    instruments[key][pair.name] = pair.id;
                });
            });
            return Object.assign({}, state, instruments);
        }
    default:
        return state;
    }
}

export default Instruments;