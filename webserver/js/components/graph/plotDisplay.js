import React from 'react';
import Line from './line';
import Bar from './bar';
import XAxis from './xaxis';
import YAxis from './yaxis';
import {scaleLinear, scaleTime, scaleOrdinal, schemeCategory10} from 'd3-scale';
import {max, min, bisector} from 'd3-array';
import {zoom} from 'd3-zoom';
import {select, event} from 'd3-selection';
import Legend from '../legend/legend.js';
import Entries from 'object.entries';

function valueIsInDomain(value, domain) {
    return value >= domain[0] && value <= domain[1];
}

function getPlotTranslation(left, top) {
    return `translate(${left}, ${top})`;
}

function getXScaleTranslation(height) {
    return `translate(0, ${height})`;
}

function getYScaleTranslation(width) {
    return `translate(${width}, 0)`;
}

class PlotDisplay extends React.Component {
    constructor(props) {
        super(props);
        this.updateZoom = this.updateZoom.bind(this);
        this.buildScale = this.buildScales.bind(this);
        this.buildItems = this.buildItems.bind(this);
        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseLeave = this.onMouseLeave.bind(this);
        this.getDataXDomain = this.getDataXDomain.bind(this);
        this.getDataYDomain = this.getDataYDomain.bind(this);

        this.buildScales(this.props.plotData);
        this.zoomGenerator = zoom().extent([[0, 0], [this.props.width * .95, this.props.height]]).translateExtent(
                [[0, 0], [this.props.width * .95, this.props.height]]).scaleExtent([1, Infinity]).on('zoom', this.updateZoom);
        this.state = {
            hoverLines: [],
            hoverValues: [],
            transformedXScale: this.xscale
        };
    }

    getDataXDomain(plotData) {
        var xMin = min(Array.from(plotData, (dataSeries) => {
            var data = dataSeries.Data;
            var minVal = data.length > 0 ? new Date(data[0].T) : new Date(2000, 1);
            return minVal;
        }));

        var xMax = max(Array.from(plotData, (dataSeries) => {
            var data = dataSeries.Data;
            var maxVal = data.length > 0 ? new Date(data[data.length - 1].T) : new Date(2010, 1);
            return maxVal;
        }));

        return [xMin, xMax];
    }

    getDataYDomain(plotData) {
        var yMin = min(Array.from(plotData, (dataSeries) => {
            var data = dataSeries.Data;
            var minVal = data.length == 0 ? 0 : min(Array.from(data, (val) => {
                return val.V;
            }));
            return minVal;
        }));

        var yMax = max(Array.from(plotData, (dataSeries) => {
            var data = dataSeries.Data;
            var maxVal = data.length == 0 ? 1000 : max(Array.from(data, (val) => {
                return val.V;
            }));
            return maxVal;
        }));

        return [yMin * 0.95, yMax * 1.05];
    }

    updateZoom() {
        this.setState({
            transformedXScale : event.transform.rescaleX(this.xscale)
        });
    }

    buildScales(plotData) {
        this.xscale = scaleTime()
            .domain(this.getDataXDomain(plotData))
            .range([0, this.props.width * .95]);
        this.yscale = scaleLinear()
            .domain(this.getDataYDomain(plotData))
            .range([this.props.height, 0]);
        this.colorscale = scaleOrdinal(schemeCategory10);
    }

    buildItems(plotData) {
        return Array.from(plotData, (dataSeries) => {
            var data = dataSeries.Data;   
            if (dataSeries.Type === 'line') {
                return (
                    <Line
                        xscale={this.state.transformedXScale}
                        yscale={this.yscale}
                        colorscale={this.colorscale}
                        dataSet={data}
                        key={dataSeries.Title}
                        colorid={dataSeries.Title}
                    />
                );
            } else if (dataSeries.Type === 'bar') {
                return (
                    <Bar
                        xscale={this.state.transformedXScale}
                        yscale={this.yscale}
                        colorscale={this.colorscale}
                        dataSet={data}
                        key={dataSeries.Title}
                        colorid={dataSeries.Title}
                    />
                );
            }
        });
    }

    onMouseMove(event) {
        var elX = event.pageX - this.refs.element.parentNode.getBoundingClientRect().left - this.props.xOffset - window.pageXOffset;
        var hoverXVal = this.state.transformedXScale.invert(elX);
        if (valueIsInDomain(hoverXVal, this.state.transformedXScale.domain())) {
            var style = {strokeWidth: '1', strokeLinecap: 'round', strokeDasharray: '5,5'};
            var lines = [
                <Line
                    xscale={this.state.transformedXScale}
                    yscale={this.yscale}
                    colorscale={this.colorscale}
                    dataSet={[{T: hoverXVal, V: 0}, {T: hoverXVal, V: this.yscale.domain()[1]}]}
                    key={'hoverLinex'}
                    colorid={'0'}
                    style={style}
                />
            ];

            var dateBisector = bisector(function(d) {
                return new Date(d.T);
            }).right;

            var hoverYVals = Array.from(this.props.plotData, (dataSeries) => {
                var data = dataSeries.Data;
                if (data.length === 0) {
                    return 0;
                }
                var index = dateBisector(data, hoverXVal);
                return data[index].V;
            });

            hoverYVals.forEach((val, index) => {
                lines.push(
                    <Line
                        xscale={this.state.transformedXScale}
                        yscale={this.yscale}
                        colorscale={this.colorscale}
                        dataSet={[{T: this.state.transformedXScale.domain()[0], V: val}, {T: this.state.transformedXScale.domain()[1], V: val}]}
                        key={`hoverLiney${index}`}
                        colorid={'0'}
                        style={style}
                    />
                );
            });

            var values = [
                <text
                    x={elX}
                    y={this.yscale.range()[0]}
                    fontFamily="sans-serif"
                    fontSize="15px"
                    fill="red"
                    key={'hovervaluex'}
                >
                    {hoverXVal.toDateString()}
                </text>
            ];
            hoverYVals.forEach((val, index) => {
                values.push(
                    <text
                        x={this.state.transformedXScale.range()[1]}
                        y={this.yscale(val)}
                        fontFamily="sans-serif"
                        fontSize="15px"
                        fill="red"
                        key={`hovervaluey${index}`}
                    >
                        {val}
                    </text>
                );
            });

            this.setState({
                hoverLines: lines,
                hoverValues: values
            });
        } else if (this.state.hoverLines.length > 0) {
            this.setState({
                hoverLines: [],
                hoverValues: []
            });
        }
    }   

    onMouseLeave() {
        this.setState({
            hoverLines: [],
            hoverValues: []
        });
    }

    componentDidMount() {
        this.refs.element.parentNode.addEventListener('mousemove', this.onMouseMove);
        this.refs.element.parentNode.addEventListener('mouseleave', this.onMouseLeave);
        select(this.refs.zoom).call(this.zoomGenerator);
    }

    componentWillUnmount() {
        this.refs.element.parentNode.removeEventListener('mousemove', this.onMouseMove);
        this.refs.element.parentNode.removeEventListener('mouseleave', this.onMouseLeave);
    }

    render() {
        var items = this.buildItems(this.props.plotData);
        return (
            <g className="plot" transform={getPlotTranslation(this.props.xOffset, this.props.yOffset)} ref="element" >
                <g ref="items" >
                    {items}
                    <XAxis key="axis" scale={this.state.transformedXScale} translate={getXScaleTranslation(this.props.height)} />
                </g>
                {this.state.hoverLines}
                {this.state.hoverValues}
                <YAxis key="yaxis" scale={this.yscale} translate={getYScaleTranslation(this.props.width * .95)} />
                <Legend xpos={this.props.width * .95} ypos={0} colorscale={this.colorscale} items={this.props.plotData} />
                <rect width={this.props.width * .95} height={this.props.height} fill="none" pointerEvents="all" ref="zoom" />
            </g>
        );
    }
}

PlotDisplay.propTypes = {
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    xOffset: React.PropTypes.number,
    yOffset: React.PropTypes.number,
    title: React.PropTypes.object,
    // plotData is an array of map object that has 3 keys: title (string), type (string) and data (array)
    plotData: React.PropTypes.array
};

export default PlotDisplay;