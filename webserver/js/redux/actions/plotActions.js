import Guid from 'guid';

export const ADD_PLOTS = 'ADD_PLOTS';
export const POSITION_PLOT = 'POSITION_PLOT';
export const ADD_DATASET_TO_PLOT = 'ADD_DATASET_TO_PLOT';

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