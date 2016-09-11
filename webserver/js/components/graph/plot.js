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
    return [0, getValueDataSetsMax(dataSets) * 1.05];
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

class Plot extends React.Component {
    constructor(props) {
        super(props);
        this.updateZoom = this.updateZoom.bind(this);
        this.buildScale = this.buildScales.bind(this);
        this.buildItems = this.buildItems.bind(this);
        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseLeave = this.onMouseLeave.bind(this);
        this.setInitialState = this.setInitialState.bind(this);

        this.buildScales();
        this.zoomGenerator = zoom().extent([[0, 0], [this.props.width * .95, this.props.height]]).translateExtent([[0, 0], [this.props.width * .95, this.props.height]]).scaleExtent([1, Infinity]).on('zoom', this.updateZoom);
        this.setInitialState();
    }

    updateZoom() {
        console.log(event.transform);
        //select(this.refs.items).attr('transform', 'translate(' + event.transform.x + ', 0) scale(' + event.transform.k + ', 1)');
        this.setState({transformedXScale : event.transform.rescaleX(this.xscale)});
    }

    buildScales() {
        this.xscale = scaleTime()
            .domain(getDataXDomain(this.props.dataSets))
            .range([0, this.props.width * .95]);
        this.yscale = scaleLinear()
            .domain(getDataYDomain(this.props.dataSets))
            .range([this.props.height, 0]);
        this.colorscale = scaleOrdinal(schemeCategory10);        
    }

    setInitialState() {
        this.state = {
            hoverLines: [],
            hoverValues: [],
            transformedXScale: this.xscale
        };
    }

    buildItems() {
        return Entries(this.props.dataSets).map((pair) => {
            if(pair[1].type === 'line')
                return <Line xscale={this.state.transformedXScale} yscale={this.yscale} colorscale={this.colorscale} dataSet={pair[1].data} key={pair[0]} colorid={pair[0]} />;
            else if(pair[1].type === 'bar')
                return <Bar xscale={this.state.transformedXScale} yscale={this.yscale} colorscale={this.colorscale} dataSet={pair[1].data} key={pair[0]} colorid={pair[0]} />;
        });
    }

    onMouseMove(event) {
        var elX = event.pageX - this.refs.element.parentNode.getBoundingClientRect().left - this.props.xOffset - window.pageXOffset;
        var xVal = this.state.transformedXScale.invert(elX);
        if(valueIsInDomain(xVal, this.state.transformedXScale.domain())) {
            var style = {strokeWidth: '1', strokeLinecap: 'round', strokeDasharray: '5,5'};
            var lines = [<Line xscale={this.state.transformedXScale} yscale={this.yscale} colorscale={this.colorscale} dataSet={[{t: xVal, v: 0}, {t: xVal, v: this.yscale.domain()[1]}]} key={'hoverLinex'} colorid={'0'} style={style} />];
            var dateBisector = bisector(function(d) {
                return new Date(d.t);
            }).right;
            var yVal = Entries(this.props.dataSets).map((pair) => {
                var index = dateBisector(pair[1].data, xVal);
                return pair[1].data[index].v;
            });

            yVal.forEach((val, index) => {
                lines.push(<Line xscale={this.state.transformedXScale} yscale={this.yscale} colorscale={this.colorscale} dataSet={[{t: this.state.transformedXScale.domain()[0], v: val}, {t: this.state.transformedXScale.domain()[1], v: val}]} key={`hoverLiney${index}`} colorid={'0'} style={style} />);
            });

            var values = [<text x={elX} y={this.yscale.range()[0]} fontFamily="sans-serif" fontSize="15px" fill="red" key={'hovervaluex'}>{xVal.toDateString()}</text>];
            yVal.forEach((val, index) => {
                values.push(<text x={this.state.transformedXScale.range()[1]} y={this.yscale(val)} fontFamily="sans-serif" fontSize="15px" fill="red" key={`hovervaluey${index}`}>{val}</text>);
            });

            this.setState({
                hoverLines: lines,
                hoverValues: values
            });
        } else if(this.state.hoverLines.length > 0) {
            this.setState({
                hoverLines: [],
                hoverValues: []
            });
        }
    }   

    onMouseLeave() {
        if(this.state.hoverLines.length > 0) {
            this.setState({
                hoverLines: [],
                hoverValues: []
            });
        }
    }

    componentDidMount() {
        this.refs.element.parentNode.addEventListener('mousemove', this.onMouseMove);
        this.refs.element.parentNode.addEventListener('mouseleave', this.onMouseLeave);
        select(this.refs.zoom).call(this.zoomGenerator);
    }

    render() {
        var items = this.buildItems();

        return (
            <g className="plot" transform={getPlotTranslation(this.props.xOffset, this.props.yOffset)} ref="element" >
                <g ref="items" >
                    {items}
                    <XAxis key="axis" scale={this.state.transformedXScale} translate={getXScaleTranslation(this.props.height)} />
                </g>
                {this.state.hoverLines}
                {this.state.hoverValues}
                <YAxis key="yaxis" scale={this.yscale} translate={getYScaleTranslation(this.props.width * .95)} />
                <Legend xpos={this.props.width * .95} ypos={0} colorscale={this.colorscale} items={this.props.dataSets} />
                <rect width={this.props.width * .95} height={this.props.height} fill="none" pointerEvents="all" ref="zoom" />
            </g>
        );
    }
}

Plot.propTypes = {
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    xOffset: React.PropTypes.number,
    dataSets: React.PropTypes.object,
    yOffset: React.PropTypes.number
};

export default Plot;