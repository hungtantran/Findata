import React from 'react';
import SearchBar from './searchbar';
import Graph from './graph/graph';
import Entries from 'object.entries';

class Workspace extends React.Component {

    constructor(props) {
        super(props);

        this.loadModelsFromJSON = this.loadModelsFromJSON.bind(this);
        this.handleSearchSubmit = this.handleSearchSubmit.bind(this);
        this.addGraph = this.addGraph.bind(this);

        this.numColumns = 48;
        this.width = screen.width * 0.90;
        this.cellSize = this.width / this.numColumns;

        this.defaultGraphWidthInCell = 15;
        this.defaultGraphHeightInCell = 10;
        this.defaultGraphContainerWidthInCell = 16;
        this.defaultGraphContainerHeightInCell = 11;

        this.graphs = {};

        var model = {}
        model["graphs"] = []

        this.state = {
            graphModel: model
        };
    }

    addGraph() {
        this.grid = $('.grid-stack').data('gridstack');
        var node = {
            x: 0,
            y: 0,
            width: 4,
            height: 15
        };
        this.grid.addWidget($('#' + (this.state.graphModel.graphs.length - 1)),
            node.x, node.y, node.width, node.height);
    }

    componentDidMount() {
        console.log("mount");
        $(function () {
            var options = {
                cellHeight: 20,
                verticalMargin: 5
            };
            $('.grid-stack').gridstack(options);
        });
    }

    componentDidUpdate() {
        console.log("update");
        this.addGraph();
    }

    render() {
        console.log("render");
        var margins = { top: 20, right: 40, bottom: 30, left: 10 };
        this.graphs = this.state.graphModel.graphs && Entries(this.state.graphModel.graphs).map((pair, index) => {
            var width = this.defaultGraphWidthInCell * this.cellSize;
            var height = this.defaultGraphHeightInCell * this.cellSize;
            return <Graph key={pair[0].Title} plots={pair[1].Plots} width={width} height={height} margins={margins} index={index}/>;
        });

        return (
            <div id="content" className='container'>
                <div className="workspace">
                    <SearchBar onSearchSubmit={this.handleSearchSubmit} />
                    <div className="grid-stack" data-gs-width="12" data-gs-animate="yes">
                        {this.graphs}
                    </div>
                </div>
            </div>
        );
    }

    loadModelsFromJSON(json) {
        var model = this.state.graphModel;
        model["graphs"].push(json);
        this.setState({
            graphModel: model
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
