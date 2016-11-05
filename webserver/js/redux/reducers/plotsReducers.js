import * as Actions from '../actions/plotActions';

function Plots(state={}, action) {
    switch(action.type) {
    case Actions.ADD_PLOTS:
        {
            let newPlots = {};
            action.plots.forEach((plot) => {
                newPlots[plot.id] = {dataSets: plot.dataSets, parent: action.parentId, x: 0, y: 0, width: 0, height: 0};
            }); 
            return Object.assign({}, state, newPlots);
        }
    case Actions.POSITION_PLOT:
        {
            let plot = Object.assign({}, state[action.id], action.position);
            return Object.assign({}, state, {[action.id]: plot});
        }
    default:
        return state;
    }
}

export default Plots;