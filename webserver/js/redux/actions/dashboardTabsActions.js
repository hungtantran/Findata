export const DASHBOARD_SAVE = 'DASHBOARD_SAVE';
export const DASHBOARD_LOAD = 'DASHBOARD_LOAD';
export const DASHBOARD_ADD = 'DASHBOARD_ADD';
export const DASHBOARD_ACTIVATE = 'DASHBOARD_ACTIVATE';

export function save() {
    return {type: DASHBOARD_SAVE};
}

export function load() {
    return {type: DASHBOARD_LOAD};
}

export function add() {
    return {type: DASHBOARD_ADD};
}

export function activate(name) {
    return {type: DASHBOARD_ACTIVATE, name};
}
