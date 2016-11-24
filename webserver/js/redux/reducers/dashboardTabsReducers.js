import * as Actions from '../actions/dashboardTabsActions';
import {ADD_ELEMENT} from '../actions/elementActions';

const initialState = {
    tabs: {'Dashboard 1': []},
    activeTab: 'Dashboard 1'
};

function tabs(newTabName, currentTabs) {
    return Object.assign({}, currentTabs, {
        [newTabName]: []
    });
}

function element(activeTab, currentTabs, newIds) {
    return Object.assign({}, currentTabs, {
        [activeTab]: newIds
    });
}

function DashboardTabs(state=initialState, action) {
    switch(action.type) {
    case Actions.DASHBOARD_ADD:
        {
            let newName = 'Dashboard ' + (Object.keys(state.tabs).length + 1);
            return Object.assign({}, state, {
                activeTab: newName,
                tabs: tabs(newName, state.tabs)
            });
        }
    case Actions.DASHBOARD_ACTIVATE:
        return Object.assign({}, state, {
            activeTab: action.name,
        });
    case ADD_ELEMENT:
        {
            let currentIds = state.tabs[state.activeTab].slice();
            currentIds.push(action.id);
            return Object.assign({}, state, {
                tabs: element(state.activeTab, state.tabs, currentIds)
            });
        }
    case Actions.LOAD_DASHBOARD_TABS:
        return Object.assign({}, action.dashboardTabs);
    default:
        return state;
    }
}

export default DashboardTabs;