export const LAYOUT_CHANGE = 'LAYOUT_CHANGE';

export function updateGridLayout(layout) {
    return {type: LAYOUT_CHANGE, layout};
}