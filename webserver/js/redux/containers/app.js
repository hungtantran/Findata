import React from 'react';
import SearchBar from './searchbar';
import DataPane from './dataPane';

const App = () => (
    <div>
        <div key='sidebar' className="col-sm-3 col-md-2">
            <SearchBar/>
            <DataPane/>
        </div>
    </div>
);

export default App;