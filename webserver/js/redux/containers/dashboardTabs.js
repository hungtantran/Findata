import React from 'react';
import { connect } from 'react-redux';
import {add, activate, load, save} from '../actions/dashboardTabsActions';

function DashboardTabs(props) {
    var tabs = props.tabs.map((tabName) => {
        var activate = () => {
            props.activate(tabName);
        };

        var active = tabName == props.activeTab ? 'active' : '';

        return <li className={active} key={tabName}><a data-toggle="tab" onClick={activate}>{tabName}</a></li>;
    });

    tabs.push(<li key='Add'><a onClick={props.add}>Add...</a></li>);

    return(
    <ul className="nav nav-tabs">
        {tabs}
        <ul className="nav navbar-nav navbar-right">
            <li><button type="button" className="btn btn-primary" onClick={props.save}>Save Dashboard</button></li>
            <li><button type="button" className="btn btn-primary" onClick={props.load}>Load Dashboard</button></li>
        </ul>
    </ul>);
}

DashboardTabs.propTypes = {
    tabs: React.PropTypes.array,
    add: React.PropTypes.func,
    activate: React.PropTypes.func,
    activeTab: React.PropTypes.string,
    save: React.PropTypes.func,
    load: React.PropTypes.func
};

function mapStateToProps(state) {
    return {
        activeTab: state.dashboardTabs.activeTab,
        tabs: Object.keys(state.dashboardTabs.tabs)
    };
}

function mapDispatchToProps(dispatch) {
    return {
        add: () => dispatch(add()),
        activate: (name) => dispatch(activate(name)),
        save: () => dispatch(save()),
        load: () => dispatch(load()),
    };
}

export default connect(mapStateToProps, mapDispatchToProps)(DashboardTabs);