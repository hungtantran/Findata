import {ADD_PLOTS} from '../actions/plotActions';

function Plots(state={}, action) {
    switch(action.type) {
    case ADD_PLOTS:
        {
            let newPlots = {};
            action.plotIds.forEach((id) => {
                newPlots[id] = {};
            });
            return Object.assign({}, state, newPlots);
        }
    default:
        return state;
    }
}

export default Plots;