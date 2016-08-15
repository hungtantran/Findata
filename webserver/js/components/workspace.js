import React from 'react';
import SearchBar from './searchbar';
import D3Graph from './graph/graph';
import Entries from 'object.entries';

class Workspace extends React.Component {

    constructor(props) {
        super(props);

        this.loadModelsFromJSON = this.loadModelsFromJSON.bind(this);
        this.handleSearchSubmit = this.handleSearchSubmit.bind(this);

        this.state = {
            graphModel: {}
        };
    }

    componentDidMount() {
    }

    componentDidUpdate() {
    }

    render() {
        var margins = { top: 50, right: 50, bottom: 50, left: 50 };
        var graphs = this.state.graphModel.graphs && Entries(this.state.graphModel.graphs).map(function(pair) {
            return <D3Graph key={pair[0]} dataSets={pair[1].dataSets} width={window.innerWidth} height={window.innerHeight} margins={margins}/>;
        });

        return (
            <div className="workspace">
                <SearchBar onSearchSubmit={this.handleSearchSubmit} />
                {graphs}
            </div>
        );
    }

    loadModelsFromJSON(json) {
        /*data.push(json.graphModel.adj_close.map(function(item) {
            return {t: new Date(item[0].replace(/-/g, '/')), v: item[1]};
        }));*/

        this.setState({
            graphModel: json.graphModel
        });
    }

    handleSearchSubmit(submission) {
        fetch($SCRIPT_ROOT + '/search' + '?search=' + submission.search, {mode: 'no-cors'})
            .then(function(response) {
                return response.json();
            }).catch(function(ex) {
                console.log('parsing failed', ex);
            }).then((json) => {
                this.loadModelsFromJSON(json);
            });
    }
}

export default Workspace;
