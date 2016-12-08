import Guid from 'guid';

export const ADD_PLOTS = 'ADD_PLOTS';
export const POSITION_PLOT = 'POSITION_PLOT';
export const ADD_DATASET_TO_PLOT = 'ADD_DATASET_TO_PLOT';
export const REMOVE_DATASET_FROM_PLOT = 'REMOVE_DATASET_FROM_PLOT';
export const REMOVE_PLOT = 'REMOVE_PLOT';

export function addPlots(plots, parentId) {
    return {type: ADD_PLOTS, plots, parentId};
}

export function createNewPlot(dataSetId, parentId) {
    let id = Guid.raw();
    let plots = [{id, dataSets:[dataSetId]}];
    return {type: ADD_PLOTS, plots, parentId};
}

export function positionPlot(id, position) {
    return {type: POSITION_PLOT, id, position};
}

export function addDataSetToPlot(dataSetId, plotId) {
    return {type: ADD_DATASET_TO_PLOT, dataSetId, plotId};
}

function removePlot(plotId, parent) {
    return {type: REMOVE_PLOT, plotId, parent};
}

function innerRemoveDataSetFromPlot(dataSetId, plotId) {
    return {type: REMOVE_DATASET_FROM_PLOT, dataSetId, plotId};
}

export function removeDataSetFromPlot(dataSetId, plotId) {
    return (dispatch, getState) => {
        let state = getState();
        if(state.plots[plotId].dataSets.length == 1 && state.plots[plotId].dataSets[0] == dataSetId) {
            let parent = state.plots[plotId].parent;
            dispatch(removePlot(plotId, parent));
        } else
            dispatch(innerRemoveDataSetFromPlot(dataSetId, plotId));
    };
}