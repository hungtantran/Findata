import React from 'react';
import SearchBar from './searchbar';
import Grid from './graph/grid';

class Workspace extends React.Component {

    constructor(props) {
        super(props);

        this.loadModelsFromJSON = this.loadModelsFromJSON.bind(this);
        this.handleSearchSubmit = this.handleSearchSubmit.bind(this);

        this.state = {
            model: []
        };
    }

    render() {
        return (
            <div id="content" className='container'>
                <div className="workspace">
                    <SearchBar onSearchSubmit={this.handleSearchSubmit} />
                    <Grid model={this.state.model} />
                </div>
            </div>
        );
    }

    loadModelsFromJSON(json) {
        var model = this.state.model;
        model.push(json);
        this.setState({
            model: model
        });
    }

    handleSearchSubmit(submission) {
        fetch($SCRIPT_ROOT + '/search', {
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
            this.loadModelsFromJSON(json);
        });
    }
}

export default Workspace;
