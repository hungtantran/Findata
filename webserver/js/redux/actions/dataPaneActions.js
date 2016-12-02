export const FILTER_CHANGE = 'FILTER_CHANGE';

export function filterChanged(tableCode, filter) {
    return {type: FILTER_CHANGE, tableCode, filter};
}
