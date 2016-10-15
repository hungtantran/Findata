import React from 'react';
import SearchBar from './searchbar';
import Grid from './grid';
import DashboardTabs from './dashboardTabs';

class Workspace extends React.Component {

    constructor(props) {
        super(props);

        this.addGraphToModel = this.addGraphToModel.bind(this);

        // Callback for Searchbar object
        this.handleSearchSubmit = this.handleSearchSubmit.bind(this);

        // Callback for Grid object
        this.saveGridToServer = this.saveGridToServer.bind(this);
        this.loadGridFromServer = this.loadGridFromServer.bind(this);
        this.saveNewGridState = this.saveNewGridState.bind(this);
        this.activateDashboard = this.activateDashboard.bind(this);
        this.addDashboard = this.addDashboard.bind(this);

        /* model is an array like this
        [{
            "id": 0,
            "x": 0,
            "y": 0,
            "width": 4,
            "height": 15,
            "graph": {
                "Title": "data_metrics",
                "Plots": {
                    "adj_close": {
                        "Title": "adj_close",
                        "DataSets": {
                            "adj_close": {
                                "Title": "adj_close",
                                "Type": "line",
                                "DataDesc": {
                                    "metricName": "adj_close",
                                    "tableName": "data_metrics"
                                }
                            }
                        }
                    },
                    "volume": {
                        "Title": "volume",
                        "DataSets": {
                            "volume": {
                                "Title": "volume",
                                "Type": "bar",
                                "DataDesc": {
                                    "metricName": "volume",
                                    "tableName": "data_metrics"
                                }
                            }
                        }
                    }
                }
            }
        }]*/
        var initialModel = {'Dashboard 1' : []};

        this.state = {
            model: initialModel,
            activeDashboard: 'Dashboard 1'
        };
        console.log(this.state);
    }
    
    // Function call to send grid information to server to save 
    saveGridToServer() {
        var gridJson = JSON.stringify(this.state.model);
        fetch($SCRIPT_ROOT + '/user', {
            credentials: 'same-origin',
            mode: 'no-cors',
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: "SaveGrid",
                grid: gridJson,
            })
        }).then(function(response) {
            return response.json();
        }).catch(function(ex) {
            console.log('parsing failed', ex);
        }).then((json) => {
            // TODO do something to indicate save successful
        });
    }

    saveNewGridState(grid) {
        // TODO validate gridJson
        this.state.model[this.state.activeDashboard] = grid;
    }

    // Function call to load the gridstack information for user
    loadGridFromServer() {
        // TODO change this to GET request
        fetch($SCRIPT_ROOT + '/user', {
            credentials: 'same-origin',
            mode: 'no-cors',
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: "LoadGrid",
            })
        }).then(function(response) {
            return response.json();
        }).catch(function(ex) {
            console.log('parsing failed', ex);
        }).then((json) => {
            var model = JSON.parse(json);
            this.setState({
                model: model
            });
        });
    }

    addGraphToModel(graph) {
        var modelElem = {};
        modelElem["id"] = -1;
        modelElem["x"] = -1;
        modelElem["y"] = -1;
        modelElem["width"] = -1;
        modelElem["height"] = -1;
        modelElem["graph"] = graph;

        var model = this.state.model;
        model[this.state.activeDashboard].push(modelElem);

        this.setState({
            model: model
        });
    }

    handleSearchSubmit(submission) {
        // TODO change this to GET request
        fetch($SCRIPT_ROOT + '/search', {
            credentials: 'same-origin',
            mode: 'no-cors',
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: "GetGraph",
                term: String(submission.term),
                type: String(submission.type),
                id: String(submission.id),
            })
        }).then(function(response) {
            return response.json();
        }).catch(function(ex) {
            console.log('parsing failed', ex);
        }).then((json) => {
            // TODO validate json
            var graph = json;
            this.addGraphToModel(graph);
        });
    }

    activateDashboard(dashboardName) {
        this.setState({activeDashboard: dashboardName});
    }

    addDashboard() {
        var currentDashboards = this.state.model;
        var dashboardName = 'Dashboard ' + (Object.keys(currentDashboards).length + 1);
        currentDashboards[dashboardName] = [];
        this.setState({
            model: currentDashboards,
            activeDashboard: dashboardName
        });
    }

    render() {
        console.log(this.state);
        return (
            <div id="content" className='container'>
                <div className="workspace">
                    <SearchBar onSearchSubmit={this.handleSearchSubmit} />
                    <DashboardTabs tabs={Object.keys(this.state.model) } activeTab={this.state.activeDashboard} onActivateDashboard={this.activateDashboard} onAddDashboard={this.addDashboard} />
                    <Grid
                        model={this.state.model[this.state.activeDashboard]}
                        saveGridToServer={this.saveGridToServer}
                        loadGridFromServer={this.loadGridFromServer}
                        saveNewGridState={this.saveNewGridState}
                    />
                </div>
            </div>
        );
    }
}

export default Workspace;


/*
SearchBar
DataList
Dashboards
    Dashboard
        Grid
    DashboardBar
        PlusButton
        DashboardTab[]
*/