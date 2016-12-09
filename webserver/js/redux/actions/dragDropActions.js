import {removeDataSetFromPlot} from './plotActions';
import {addDataSetToPlot, createNewPlot} from '../actions/plotActions';

export const DRAG_START = 'DRAG_START';
export const DROP = 'DROP';
export const DRAG_END = 'DRAG_END';

export function startDrag(sourceInfo) {
    return {type: DRAG_START, sourceInfo};
}

export function drop(targetInfo) {
    return {type: DROP, targetInfo};
}

export function endDrag() {
    return (dispatch, getState) => {
        let state = getState();
        let dragDropState = state.dragDrop;
        let targetInfo = dragDropState.targetInfo;
        let sourceInfo = dragDropState.sourceInfo;

        if(sourceInfo) {
            if(sourceInfo.source == 'legend' && !sourceInfo.control && (!targetInfo || targetInfo.plotId != sourceInfo.plotId))
                dispatch(removeDataSetFromPlot(sourceInfo.dataSetId, sourceInfo.plotId));

            if(targetInfo) {
                if(targetInfo.target == 'plot' && (!sourceInfo.plotId || (sourceInfo.plotId != targetInfo.plotId)))
                    dispatch(addDataSetToPlot(sourceInfo.dataSetId, targetInfo.plotId));

                if(targetInfo.target == 'element')
                    dispatch(createNewPlot(sourceInfo.dataSetId, targetInfo.elementId));
            }
        }

        dispatch({type: DRAG_END});
    };
}

