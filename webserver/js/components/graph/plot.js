import React from 'react';
import Line from './line';
import Bar from './bar';
import XAxis from './xaxis';
import YAxis from './yaxis';
import {scaleLinear, scaleTime, scaleOrdinal, schemeCategory10} from 'd3-scale';
import {max, min} from 'd3-array';
import Legend from '../legend/legend.js';

function getDataXDomain(dataSets) {
    return [
        min(dataSets, function (dataSet) {
            return dataSet[0].t;
        }),
        max(dataSets, function (dataSet) {
            return dataSet[dataSet.length - 1].t;
        })
    ];
}

function getValueDataSetsMax(dataSets) {
    return max(dataSets, function (dataSet) {
        return max(dataSet, function (d) {
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
    var lines = props.dataSets.map(function (dataSet, index) {
        return <Line xscale={scales.xscale} yscale={scales.yscale} colorscale={scales.colorscale} dataSet={dataSet} key={index} colorid={index} />;
    });
    var bars = props.dataSets.map(function (dataSet, index) {
        return <Bar xscale={scales.xscale} yscale={scales.yscale} colorscale={scales.colorscale} dataSet={dataSet} key={index} colorid={index} />;
    });

    return (
        <g className="plot" transform={getPlotTranslation(props.margins.left, props.margins.top) } >
            {lines}
            //{bars}
            <XAxis key="axis" scale={scales.xscale} translate={getXScaleTranslation(props.height) } />
            <YAxis key="yaxis" scale={scales.yscale} />
            <Legend xpos= {props.width * .95} ypos={0} colorscale={scales.colorscale} items={props.dataSets} />
        </g>
    );
}

Plot.propTypes = {
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    margins: React.PropTypes.object,
    dataSets: React.PropTypes.array
};

export default Plot;