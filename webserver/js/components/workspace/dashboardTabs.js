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
    </ul>);
}

DashboardTabs.propTypes = {
    tabs: React.PropTypes.array,
    onAddDashboard: React.PropTypes.func,
    onActivateDashboard: React.PropTypes.func,
    activeTab: React.PropTypes.string
};

export default DashboardTabs;