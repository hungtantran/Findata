import {LAYOUT_CHANGE} from '../actions/gridActions';
import {ADD_ELEMENT} from '../actions/elementActions';
import {ADD_PLOTS} from '../actions/plotActions';

function Elements(state={}, action) {
    switch(action.type) {
    case LAYOUT_CHANGE:
        {
            let layout = action.layout;
            Object.keys(layout).forEach((id) => {
                layout[id].plots = state[id].plots;
            });
            return Object.assign({}, state, layout);
        }
    case ADD_ELEMENT:
        {
            let x = 0, y = 0, width = 0, height = 0;
            return Object.assign({}, state, {[action.id]:{x, y, width, height, plots: []}});   
        }
    case ADD_PLOTS:
        // TODO don't duplicate the plots
        {
            let plots = state[action.parentId].plots.slice();
            let {x, y, width, height} = state[action.parentId];
            action.plots.forEach((plot) => {
                plots.push(plot.id);
            });
            return Object.assign({}, state, {[action.parentId]: { plots, x, y, width, height}});   
        }
    default:
        return state;
    }
}

export default Elements;