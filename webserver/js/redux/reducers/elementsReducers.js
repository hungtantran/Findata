import {LAYOUT_CHANGE} from '../actions/gridActions';
import {ADD_ELEMENT} from '../actions/elementActions';
import {ADD_PLOTS, REMOVE_PLOT} from '../actions/plotActions';
import {scaleOrdinal, schemeCategory10} from 'd3-scale';
import {LOAD_ELEMENTS} from '../actions/dashboardTabsActions';

function Elements(state={}, action) {
    switch(action.type) {
    case LAYOUT_CHANGE:
        {
            let layout = action.layout;
            Object.keys(layout).forEach((id) => {
                layout[id].plots = state[id].plots;
                layout[id].colorScale = state[id].colorScale;
            });
            return Object.assign({}, state, layout);
        }
    case ADD_ELEMENT:
        {
            let x = 0, y = 0, width = 0, height = 0;
            let colorScale = scaleOrdinal(schemeCategory10);
            return Object.assign({}, state, {[action.id]:{x, y, width, height, plots: [], colorScale}});   
        }
    case ADD_PLOTS:
        // TODO don't duplicate the plots
        {
            let plots = state[action.parentId].plots.slice();
            let {x, y, width, height, colorScale} = state[action.parentId];
            action.plots.forEach((plot) => {
                plots.push(plot.id);
            });
            return Object.assign({}, state, {[action.parentId]: { plots, x, y, width, height, colorScale}});   
        }
    case LOAD_ELEMENTS:
        return Object.assign({}, action.elements);
    case REMOVE_PLOT:
        {
            let newPlots = state[action.parent].plots.filter((id) => {
                return id != action.plotId;
            });            

            if(newPlots.length == state[action.parent].plots.length)
                return state;

            let element = Object.assign({}, state[action.parent], {plots : newPlots});
            return Object.assign({}, state, {[action.parent]: element});
        }
    default:
        return state;
    }
}

export default Elements;