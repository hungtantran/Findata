import React from 'react';
import DashboardTabs from './dashboardTabs';
import Grid from './grid';

class Dashboards extends React.Component {
    constructor(props) {
        super(props);

        var initialDashName = 'Dashboard 1';

        this.state = {
            dashboardMap: {initialDashName : <Grid saveNewGridState={this.props.onLayoutChange} />},
            activeDashboard: initialDashName
        };
    }

    activateDashboard(dashboardName) {
        this.setState({activeDashboard: dashboardName});
    }

    addDashboard() {
        var currentDashboards = this.state.dashboardMap;
        var dashboardName = 'Dashboard ' + (this.state.dashboardMap.size() + 1);
        currentDashboards[dashboardName] = <Grid saveNewGridState={this.props.onLayoutChange} />;
        this.setState({
            dashboardMap: currentDashboards,
            activateDashboard: dashboardName
        });
    }

    render() {
        return <div>
            <DashboardTabs tabs={Object.keys(this.state.dashboardMap) } onActivateDashboard={this.activateDashboard} onAddDashboard={this.addDashboard} />
            {this.state.dashboardMap[this.state.activeDashboard]}
        </div>;
    }
}

Dashboards.propTypes = {
    model: React.PropTypes.Object,
    onLayoutChange: React.PropTypes.func,
};

export default Dashboards;