export const ADD_PLOTS = 'ADD_PLOTS';
export const POSITION_PLOT = 'POSITION_PLOT';

export function addPlots(plots, parentId) {
    return {type: ADD_PLOTS, plots, parentId};
}

export function positionPlot(id, position) {
    return {type: POSITION_PLOT, id, position};
}