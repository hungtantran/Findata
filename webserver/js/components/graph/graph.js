import React from 'react';
import Plot from './plot';
import Entries from 'object.entries';

function getPlotProps(dataSets, width, height, xOffset, yOffset, key, margins) {
    var innerWidth = width - margins.right - margins.left;

    return {
        dataSets: dataSets, width: innerWidth, height: height, xOffset: xOffset, yOffset: yOffset, key: key};
}

class Graph extends React.Component {
    constructor(props) {
        super(props);
        this.buildPlots = this.buildPlots.bind(this);

        this.buildPlots();
    }

    buildPlots() {
        var innerHeight = this.props.height - this.props.margins.top - this.props.margins.bottom;
        var plotCount = Object.keys(this.props.plots).length;
        var plotHeight = innerHeight / plotCount;
        this.state = {plots: Entries(this.props.plots).map((pair, index) => {
            var yOffset = this.props.margins.top + plotHeight * index;
            return <Plot {...getPlotProps(pair[1].DataSets, this.props.width, plotHeight, this.props.margins.left, yOffset, pair[0], this.props.margins) } />;
        })};
    }

    render() {
        return (
            <div className="grid-stack-item" id={this.props.index}>
                <div className="grid-stack-item-content">
                    <svg className="graph" width={this.props.width} height={this.props.height} style={this.props.style} > 
                        {this.state.plots}
                    </svg>
                </div>
            </div>
        );
    }
}

Graph.propTypes = { 
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    margins: React.PropTypes.object,
    plots: React.PropTypes.object,
    style: React.PropTypes.object,
};

export default Graph;