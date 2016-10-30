export const ADD_PLOTS = 'ADD_PLOTS';

export function addPlots(plotIds, parentId) {
    return {type: ADD_PLOTS, plotIds, parentId};
}