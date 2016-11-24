import {scaleOrdinal, schemeCategory10} from 'd3-scale';

export const DASHBOARD_SAVE = 'DASHBOARD_SAVE';
export const DASHBOARD_LOAD = 'DASHBOARD_LOAD';
export const DASHBOARD_ADD = 'DASHBOARD_ADD';
export const DASHBOARD_ACTIVATE = 'DASHBOARD_ACTIVATE';

export const LOAD_DASHBOARD_TABS = 'LOAD_DASHBOARD_TABS';
export const LOAD_DATASETS = 'LOAD_DATASETS';
export const LOAD_ELEMENTS = 'LOAD_ELEMENTS';
export const LOAD_INSTRUMENTS = 'LOAD_INSTRUMENTS';
export const LOAD_PLOTS = 'LOAD_PLOTS';
export const LOAD_SEARCHBAR = 'LOAD_SEARCHBAR';

function requestSave() {
    return {type: DASHBOARD_SAVE};
}

function requestLoad() {
    return {type: DASHBOARD_LOAD};
}

function saveDashboard(dispatch, getState) {
    let state = getState();
    var grid = Object.assign({}, state);
    var dataSets = grid['dataSets'];
    Object.keys(dataSets).forEach((id) => {
        dataSets[id].data = [];
        dataSets[id].domain = [];
        dataSets[id].range = [];
        dataSets[id].isFetching = false;
    });
    grid['searchBar'].isFetchingSuggestions = false;
    grid['searchBar'].currentSearch = '';
    var gridJson = JSON.stringify(grid);

    dispatch(requestSave());
    return fetch($SCRIPT_ROOT + '/user', {
        credentials: 'same-origin',
        mode: 'no-cors',
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: 'SaveGrid',
            grid: gridJson,
        })
    }).then(function(response) {
        return response.json();
    }).catch(function(ex) {
        console.log('parsing failed', ex);
    }).then((json) => {
        console.log('Save successfully');
    });
}

function loadDashboard(dispatch, getState) {
    dispatch(requestLoad());
    return fetch($SCRIPT_ROOT + '/user', {
        credentials: 'same-origin',
        mode: 'no-cors',
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: 'LoadGrid',
        })
    }).then(function(response) {
        return response.json();
    }).catch(function(ex) {
        console.log('parsing failed', ex);
    }).then((json) => {
        let savedState = JSON.parse(json);
        let {dashboardTabs, dataSets, elements, instruments, plots, searchBar} = savedState;
        if (dashboardTabs === undefined ||
            dataSets === undefined) {
            return;
        }
        Object.keys(elements).forEach((id) => {
            elements[id].colorScale = scaleOrdinal(schemeCategory10);
        });
        dispatch(loadSearchBar(searchBar));
        dispatch(loadInstruments(instruments));
        dispatch(loadDataSets(dataSets));
        dispatch(loadPlots(plots));
        dispatch(loadElements(elements));
        dispatch(loadDashboardTabs(dashboardTabs));
    });
}

// TODO move these to other action files
function loadDashboardTabs(dashboardTabs) {
    return {type: LOAD_DASHBOARD_TABS, dashboardTabs};
}

function loadDataSets(dataSets) {
    return {type: LOAD_DATASETS, dataSets};
}

function loadElements(elements) {
    return {type: LOAD_ELEMENTS, elements};
}

function loadInstruments(instruments) {
    return {type: LOAD_INSTRUMENTS, instruments};
}

function loadPlots(plots) {
    return {type: LOAD_PLOTS, plots};
}

function loadSearchBar(searchBar) {
    return {type: LOAD_SEARCHBAR, searchBar};
}

export function save() {
    return saveDashboard;
}

export function load() {
    return loadDashboard;
}

export function add() {
    return {type: DASHBOARD_ADD};
}

export function activate(name) {
    return {type: DASHBOARD_ACTIVATE, name};
}
