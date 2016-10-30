import React from 'react';
import SearchBar from './searchbar';
import DataPane from './dataPane';
import DashboardTabs from './dashboardTabs';

const App = () => (
    <div>
        <div key='sidebar' className="col-sm-3 col-md-2">
            <SearchBar/>
            <DataPane/>
        </div>
        <div key='main' className="col-sm-9 col-md-10">
            <DashboardTabs/>
        </div>
    </div>
);

export default App;