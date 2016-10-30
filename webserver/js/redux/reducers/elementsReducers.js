import {LAYOUT_CHANGE} from '../actions/gridActions';
import {ADD_ELEMENT} from '../actions/elementActions';

function Elements(state={}, action) {
    switch(action.type) {
    case LAYOUT_CHANGE:
        return Object.assign({}, state, action.layout);
    case ADD_ELEMENT:
        {
            let x = -1, y = -1, width = -1, height = -1;
            return Object.assign({}, state, {[action.id]:{x, y, width, height}});   
        }
    default:
        return state;
    }
}

export default Elements;