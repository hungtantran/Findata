import React from 'react';
import Plot from './plot';

function getPlotProps(dataSets, width, height, margins, key) {
    var innerWidth = width - margins.right - margins.left;
    var innerHeight = height - margins.top - margins.bottom;

    return {
        dataSets: dataSets, width: innerWidth, height: innerHeight, margins: margins, key: key};
}

function Graph(props) {
    return ( 
        <svg className="graph" width={props.width}  height={props.height} > 
            <Plot {...getPlotProps(props.dataSets, props.width, props.height, props.margins, 'plot') } />
        </svg>
    );
}

Graph.propTypes = { 
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    margins: React.PropTypes.object,
    dataSets: React.PropTypes.array
};

export default Graph;