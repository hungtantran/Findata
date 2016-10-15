import React from 'react';
import Graph from '../graph/graph';
import Entries from 'object.entries';

class Grid extends React.Component {
    constructor(props) {
        super(props);

        this.saveGrid = this.saveGrid.bind(this);
        this.loadGrid = this.loadGrid.bind(this);
        this.addGraph = this.addGraph.bind(this);
        this.exportGraphState = this.exportGraphState.bind(this);

        this.numColumns = 48;
        this.width = screen.width * 0.90;
        this.cellSize = this.width / this.numColumns;

        this.defaultGraphWidthInCell = 15;
        this.defaultGraphHeightInCell = 10;
        this.defaultGraphContainerWidthInCell = 16;
        this.defaultGraphContainerHeightInCell = 11;
    }

    // Function call to serialize the current gridstack information and send to workspace
    exportGraphState() {
        var res = [];
        _.map($('.grid-stack .grid-stack-item:visible'), function (el) {
            el = $(el);
            var node = el.data('_gridstack_node');
            if (node === undefined) {
                return;
            }
            
            var graphIndex = el.attr('id');
            var graphMetadata = this.props.model[graphIndex].graph;
            res.push({
                id: parseInt(graphIndex),
                x: node.x,
                y: node.y,
                width: node.width,
                height: node.height,
                graph: graphMetadata,
            });
        }.bind(this));
        this.props.saveNewGridState(res);
    }

    // Function call to save the gridstack information for user and send to server
    saveGrid() {
        this.props.saveGridToServer();
    }

    // Function call to load the gridstack information for user
    loadGrid() {
        this.props.loadGridFromServer();
    }

    // Function call when there is new update to the dom to add new graph to the gridstacl
    // TODO: in the future, thing change doesn't mean new graph
    addGraph() {
        var grid = $('.grid-stack').data('gridstack');
        grid.removeAll();

        this.props.model.forEach((modelElem, index) => {
            var x = modelElem.x < 0 ? 0 : modelElem.x;
            var y = modelElem.y < 0 ? 0 : modelElem.y;
            var width = modelElem.width < 0 ? 4 : modelElem.width;
            var height = modelElem.height < 0 ? 15 : modelElem.height;
            var node = {
                x: x,
                y: y,
                width: width,
                height: height,
            };
            grid.addWidget(
                $('#' + index),
                node.x,
                node.y,
                node.width,
                node.height);
        });
    }

    componentDidMount() {
        $(function () {
            var options = {
                cellHeight: 20,
                verticalMargin: 5
            };
            $('.grid-stack').gridstack(options);
        });

        $('.grid-stack').on('change', this.exportGraphState);
    }

    componentDidUpdate() {
        this.addGraph();
    }

    render() {
        var margins = { top: 20, right: 40, bottom: 30, left: 10 };
        var graphs = this.props.model && Array.from(this.props.model, (graphJson, index) => {
            var width = this.defaultGraphWidthInCell * this.cellSize;
            var height = this.defaultGraphHeightInCell * this.cellSize;
            // TODO random as key is not good, quite inefficient
            return (
                <Graph
                    key={Math.random()}
                    plots={graphJson.graph.Plots}
                    width={width}
                    height={height}
                    margins={margins}
                    index={index}
                />
            );
        });

        return (
            <div>
                <button type="button" className="btn btn-primary" onClick={this.saveGrid}>Save Dashboard</button>
                <button type="button" className="btn btn-primary" onClick={this.loadGrid}>Load Dashboard</button>
                <div className="grid-stack" data-gs-width="12" data-gs-animate="yes">
                    {graphs}
                </div>
            </div>
        );
    }
}

export default Grid;