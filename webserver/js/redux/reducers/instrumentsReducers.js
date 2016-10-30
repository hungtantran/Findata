import {RECEIVE_SEARCH} from '../actions/searchBarActions';

function Instruments(state={}, action) {
    switch(action.type) {
    case RECEIVE_SEARCH:
        return Object.assign({}, state, action.results);
    default:
        return state;
    }
}

export default Instruments;