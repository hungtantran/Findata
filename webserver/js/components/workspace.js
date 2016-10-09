import React from 'react';
import SearchBar from './searchbar';
import Grid from './graph/grid';

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
        this.state = {
            model: []
        };
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
        this.state.model = grid;
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
        model.push(modelElem);
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

    render() {
        return (
            <div id="content" className='container'>
                <div className="workspace">
                    <SearchBar onSearchSubmit={this.handleSearchSubmit} />
                    <Grid
                        model={this.state.model}
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
