import React from 'react';
import Plot from './plot';
import Entries from 'object.entries';

function getPlotProps(dataSets, width, height, xOffset, yOffset, key, margins) {
    var innerWidth = width - margins.right - margins.left;

    return {
        dataSets: dataSets, width: innerWidth, height: height, xOffset: xOffset, yOffset: yOffset, key: key};
}

function Graph(props) {
    var innerHeight = props.height - props.margins.top - props.margins.bottom;
    var plotCount = Object.keys(props.plots).length;
    var plotHeight = innerHeight / plotCount;
    var plots = Entries(props.plots).map(function(pair, index) {
        var yOffset = props.margins.top + plotHeight*index;
        return <Plot {...getPlotProps(pair[1].dataSets, props.width, plotHeight, props.margins.left, yOffset, pair[0], props.margins) } />;
    });

    return ( 
        <svg className="graph" width={props.width} height={props.height} style={props.style}> 
            {plots}
        </svg>
    );
}

Graph.propTypes = { 
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    margins: React.PropTypes.object,
    plots: React.PropTypes.object,
    style: React.PropTypes.object,
};

export default Graph;