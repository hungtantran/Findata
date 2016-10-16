import React from 'react';

function DashboardTabs(props) {
    var tabs = props.tabs.map((tabName) => {
        var activate = () => {
            props.onActivateDashboard(tabName);
        };

        var active = tabName == props.activeTab ? 'active' : '';

        return <li className={active} key={tabName}><a data-toggle="tab" onClick={activate}>{tabName}</a></li>;
    });

    tabs.push(<li key='Add'><a onClick={props.onAddDashboard}>Add...</a></li>);

    return(
    <ul className="nav nav-tabs">
        {tabs}
        <ul className="nav navbar-nav navbar-right">
            <li><button type="button" className="btn btn-primary" onClick={props.saveGridToServer}>Save Dashboard</button></li>
            <li><button type="button" className="btn btn-primary" onClick={props.loadGridFromServer}>Load Dashboard</button></li>
        </ul>
    </ul>);
}

DashboardTabs.propTypes = {
    tabs: React.PropTypes.array,
    onAddDashboard: React.PropTypes.func,
    onActivateDashboard: React.PropTypes.func,
    activeTab: React.PropTypes.string,
    saveGridToServer: React.PropTypes.func,
    loadGridFromServer: React.PropTypes.func
};

export default DashboardTabs;