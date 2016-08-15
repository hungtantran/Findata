import React from 'react';
import SearchBar from './searchbar';
import D3Graph from './graph/graph';

class Workspace extends React.Component {

    constructor(props) {
        super(props);

        this.loadModelsFromJSON = this.loadModelsFromJSON.bind(this);
        this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
        this.generateData = this.generateData.bind(this);

        this.dataSets = [];

        this.state = {
            graphModel: this.generateData()
        };
    }

    componentDidMount() {
    }

    componentDidUpdate() {
    }

    render() {
        var margins = { top: 50, right: 50, bottom: 50, left: 50 };
        return (
            <div className="workspace">
                <SearchBar onSearchSubmit={this.handleSearchSubmit} />
                <D3Graph key="graph" dataSets={this.state.graphModel} width={window.innerWidth} height={window.innerHeight} margins={margins}/>
            </div>
        );
    }

    generateData() {
        var dataSet = [];
        var now = Date.now();
        var dayOffset = 1000 * 60 * 60 * 24;

        for (var i = 0; i < 200; i++) {
            dataSet.push({ t: new Date(now + i * dayOffset), v: Math.random() * i });
        }

        this.dataSets.push(dataSet);

        return this.dataSets;
    }

    loadModelsFromJSON(json) {
        var data = [];
        data.push(json.graphModel.adj_close.map(function(item) {
            return {t: new Date(item[0].replace(/-/g, '/')), v: item[1]};
        }));

        data.push(json.graphModel.vol.map(function(item) {
            return {t: new Date(item[0].replace(/-/g, '/')), v: item[1]};
        }));

        this.setState({
            graphModel: data
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
