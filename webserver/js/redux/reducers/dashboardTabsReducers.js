import * as Actions from '../actions/dashboardTabsActions';

const initialState = {
    tabs: ['Dashboard 1'],
    activeTab: 'Dashboard 1'
};

function DashboardTabs(state=initialState, action) {
    switch(action.type) {
    case Actions.DASHBOARD_ADD:
        var currentTabs = state.tabs.slice();
        var newName = 'Dashboard ' + (currentTabs.length + 1);
        currentTabs.push(newName);
        return Object.assign({}, state, {
            activeTab: newName,
            tabs: currentTabs
        });
    case Actions.DASHBOARD_ACTIVATE:
        return Object.assign({}, state, {
            activeTab: action.name,
        });
    default:
        return state;
    }
}

export default DashboardTabs;