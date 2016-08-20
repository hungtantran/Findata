import React from 'react';
import Line from './line';
import Bar from './bar';
import XAxis from './xaxis';
import YAxis from './yaxis';
import {scaleLinear, scaleTime, scaleOrdinal, schemeCategory10} from 'd3-scale';
import {max, min} from 'd3-array';
import Legend from '../legend/legend.js';
import Entries from 'object.entries';


function getDataXDomain(dataSets) {
    return [
        min(Entries(dataSets), function (pair) {
            return new Date(pair[1].data[0].t);
        }),
        max(Entries(dataSets), function (pair) {
            return new Date(pair[1].data[pair[1].data.length - 1].t);
        })
    ];
}

function getValueDataSetsMax(dataSets) {
    return max(Entries(dataSets), function (pair) {
        return max(pair[1].data, function (d) {
            return d.v;
        });
    });
}

function getDataYDomain(dataSets) {
    return [0, getValueDataSetsMax(dataSets)];
}

function buildScales(dataSets, width, height) {
    var xScale = scaleTime()
        .domain(getDataXDomain(dataSets))
        .range([0, width]);
    var yScale = scaleLinear()
        .domain(getDataYDomain(dataSets))
        .range([height, 0]);
    var colorScale = scaleOrdinal(schemeCategory10);
    return {
        xscale: xScale,
        yscale: yScale,
        colorscale: colorScale
    };
}

function getPlotTranslation(left, top) {
    return `translate(${left}, ${top})`;
}

function getXScaleTranslation(height) {
    return `translate(0, ${height})`;
}

function Plot(props) {
    var scales = buildScales(props.dataSets, props.width * .95, props.height);
    var items = Entries(props.dataSets).map(function (pair) {
        if(pair[1].type === 'line')
            return <Line xscale={scales.xscale} yscale={scales.yscale} colorscale={scales.colorscale} dataSet={pair[1].data} key={pair[0]} colorid={pair[0]} />;
        else if(pair[1].type === 'bar')
            return <Bar xscale={scales.xscale} yscale={scales.yscale} colorscale={scales.colorscale} dataSet={pair[1].data} key={pair[0]} colorid={pair[0]} />;
    });

    return (
        <g className="plot" transform={getPlotTranslation(props.xOffset, props.yOffset) } >
            {items}
            <XAxis key="axis" scale={scales.xscale} translate={getXScaleTranslation(props.height) } />
            <YAxis key="yaxis" scale={scales.yscale} />
            <Legend xpos= {props.width * .95} ypos={0} colorscale={scales.colorscale} items={props.dataSets} />
        </g>
    );
}

Plot.propTypes = {
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    xOffset: React.PropTypes.number,
    dataSets: React.PropTypes.object,
    yOffset: React.PropTypes.number
};

export default Plot;