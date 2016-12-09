import * as Actions from '../actions/dragDropActions';

function DragDrop(state={dragging: false}, action) {
    switch(action.type) {
    case Actions.DROP:
        return Object.assign({}, state, {targetInfo: action.targetInfo});
    case Actions.DRAG_END:
        return {dragging: false};
    case Actions.DRAG_START:
        {
            let sourceInfo = action.sourceInfo;
            return {dragging: true, sourceInfo};
        }
    default:
        return state;
    }
}

export default DragDrop;