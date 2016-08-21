import React from 'react';
import SearchBar from './searchbar';
import Graph from './graph/graph';
import Entries from 'object.entries';

class Workspace extends React.Component {

    constructor(props) {
        super(props);

        this.loadModelsFromJSON = this.loadModelsFromJSON.bind(this);
        this.handleSearchSubmit = this.handleSearchSubmit.bind(this);

        this.numColumns = 12;
        this.width = window.innerWidth;
        this.cellSize = this.width / this.numColumns;

        this.defaultGraphWidthInCell = 6;
        this.defaultGraphHeightInCell = 6;

        this.graphs = {};

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
        this.graphs = this.state.graphModel.graphs && Entries(this.state.graphModel.graphs).map((pair, index) => {
            var xOffset = (index % 2) * this.defaultGraphWidthInCell * this.cellSize;
            var yOffset = Math.floor(index / 2) * this.defaultGraphHeightInCell * this.cellSize;
            var width = this.defaultGraphWidthInCell * this.cellSize;
            var height = this.defaultGraphHeightInCell * this.cellSize;

            var divStyle = {
                position: 'absolute',
                left: `${xOffset}px`,
                top: `${yOffset}px`,
            };
            return <Graph key={pair[0]} plots={pair[1].plots} width={width} height={height} margins={margins} style={divStyle}/>;
        });

        return (
            <div className="workspace">
                <SearchBar onSearchSubmit={this.handleSearchSubmit} />
                <div style={{position:'relative'}}>{this.graphs}</div>
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
