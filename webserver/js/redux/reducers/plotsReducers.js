import * as Actions from '../actions/plotActions';
import {LOAD_PLOTS} from '../actions/dashboardTabsActions';

function Plots(state={}, action) {
    switch(action.type) {
    case Actions.ADD_PLOTS:
        {
            let newPlots = {};
            action.plots.forEach((plot) => {
                newPlots[plot.id] = {
                    dataSets: plot.dataSets,
                    parent: action.parentId,
                    x: 0,
                    y: 0,
                    width: 0,
                    height: 0};
            }); 
            return Object.assign({}, state, newPlots);
        }
    case Actions.POSITION_PLOT:
        {
            let plot = Object.assign({}, state[action.id], action.position);
            return Object.assign({}, state, {[action.id]: plot});
        }
    case LOAD_PLOTS:
        return Object.assign({}, action.plots);
    case Actions.ADD_DATASET_TO_PLOT:
        {
            let currentDataSets = state[action.plotId].dataSets.slice();
            if(currentDataSets.indexOf(action.dataSetId) >= 0)
                return state;
            currentDataSets.push(action.dataSetId);
            let plot = Object.assign({}, state[action.plotId], {dataSets : currentDataSets});
            return Object.assign({}, state, {[action.plotId]: plot});
        }
    case Actions.REMOVE_DATASET_FROM_PLOT:
        {
            // just remove first one. Super hack, hahah.
            let foundOne = false;
            let newDataSets = state[action.plotId].dataSets.filter((id) => {
                if(id == action.dataSetId && !foundOne) {
                    foundOne = true;
                    return false;
                }

                return true;
            });            
            if(newDataSets.length == state[action.plotId].dataSets.length)
                return state;

            let plot = Object.assign({}, state[action.plotId], {dataSets : newDataSets});
            return Object.assign({}, state, {[action.plotId]: plot});
        }
    case Actions.REMOVE_PLOT:
        {
            let newState = Object.assign({}, state);
            delete newState[action.plotId];
            return newState;
        }
    default:
        return state;
    }
}

export default Plots;