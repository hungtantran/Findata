import React from 'react';
import SearchBar from './searchbar';
import Grid from './graph/grid';

class Workspace extends React.Component {

    constructor(props) {
        super(props);

        this.saveGridToServer = this.saveGridToServer.bind(this);
        this.loadGridFromServer = this.loadGridFromServer.bind(this);
        this.addJsonToModel = this.addJsonToModel.bind(this);
        this.handleSearchSubmit = this.handleSearchSubmit.bind(this);

        this.state = {
            model: []
        };
    }
    
    // Function call to send grid information to server to save 
    saveGridToServer(gridJson) {
        console.log(gridJson);
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
            console.log("Save response", json);
        });
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
            console.log("Load grid", json);
            this.setState({
                model: json
            });
        });
    }

    addJsonToModel(json) {
        var model = this.state.model;
        model.push(json);
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
            this.addJsonToModel(json);
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
                    />
                </div>
            </div>
        );
    }
}

export default Workspace;
