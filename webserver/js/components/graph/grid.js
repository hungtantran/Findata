import React from 'react';
import Graph from './graph';
import Entries from 'object.entries';

class Grid extends React.Component {
    constructor(props) {
        super(props);

        this.saveGrid = this.saveGrid.bind(this);
        this.addGraph = this.addGraph.bind(this);

        this.numColumns = 48;
        this.width = screen.width * 0.90;
        this.cellSize = this.width / this.numColumns;

        this.defaultGraphWidthInCell = 15;
        this.defaultGraphHeightInCell = 10;
        this.defaultGraphContainerWidthInCell = 16;
        this.defaultGraphContainerHeightInCell = 11;
    }

    // Function call when there is new update to the dom to add new graph to the gridstacl
    // TODO: in the future, thing change doesn't mean new graph
    addGraph() {
        this.grid = $('.grid-stack').data('gridstack');
        var node = {
            x: 0,
            y: 0,
            width: 4,
            height: 15
        };
        this.grid.addWidget($('#' + (this.props.model.length - 1)),
            node.x, node.y, node.width, node.height);
    }

    // Function call to save the gridstack information for user and send to server
    saveGrid() {
        var res = _.map($('.grid-stack .grid-stack-item:visible'), function (el) {
            el = $(el);
            var node = el.data('_gridstack_node');
            var graphIndex = el.attr('id');
            var graphMetadata = this.props.model[graphIndex];
            return {
                id: graphIndex,
                graph: graphMetadata,
                x: node.x,
                y: node.y,
                width: node.width,
                height: node.height
            };
        }.bind(this));
    }

    componentDidMount() {
        $(function () {
            var options = {
                cellHeight: 20,
                verticalMargin: 5
            };
            $('.grid-stack').gridstack(options);
        });
    }

    componentDidUpdate() {
        this.addGraph();
    }

    render() {
        var margins = { top: 20, right: 40, bottom: 30, left: 10 };
        var graphs = this.props.model && Entries(this.props.model).map((pair, index) => {
            var width = this.defaultGraphWidthInCell * this.cellSize;
            var height = this.defaultGraphHeightInCell * this.cellSize;
            return <Graph key={pair[0].Title} plots={pair[1].Plots} width={width} height={height} margins={margins} index={index}/>;
        });

        return (
            <div>
                <button type="button" className="btn btn-primary" onClick={this.saveGrid}>Save Dashboard</button>
                <div className="grid-stack" data-gs-width="12" data-gs-animate="yes">
                    {graphs}
                </div>
            </div>
        );
    }
}

export default Grid;