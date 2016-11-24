import {connect} from 'react-redux';
import React from 'react';
import SearchBar from './searchbar';
import DataPane from './dataPane';
import DashboardTabs from './dashboardTabs';
import Grid from './grid';

import {load} from '../actions/dashboardTabsActions';

class App extends React.Component {
    componentDidMount() {
        this.props.dispatch(load());
    }

    render() {
        return (
            <div>
                <div key='sidebar' className="col-sm-3 col-md-2">
                    <SearchBar/>
                    <DataPane/>
                </div>
                <div key='main' className="col-sm-9 col-md-10">
                    <DashboardTabs/>
                    <Grid/>
                </div>
            </div>);
    }
}

App.propTypes = {
    dispatch: React.PropTypes.func,
};

export default connect()(App);