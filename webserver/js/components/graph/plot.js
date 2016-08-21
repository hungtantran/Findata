import React from 'react';
import Line from './line';
import Bar from './bar';
import XAxis from './xaxis';
import YAxis from './yaxis';
import {scaleLinear, scaleTime, scaleOrdinal, schemeCategory10} from 'd3-scale';
import {max, min} from 'd3-array';
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

class Plot extends React.Component {
    constructor(props) {
        super(props);
        this.buildScale = this.buildScales.bind(this);
        this.buildItems = this.buildItems.bind(this);
        this.onMouseMoveEvent = this.onMouseMoveEvent.bind(this);

        this.buildScales();
        this.buildItems();
        this.props.mouseEventsRegister(this.onMouseMoveEvent);
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

    buildItems() {
        this.state = {
            items:
            Entries(this.props.dataSets).map((pair) => {
                if(pair[1].type === 'line')
                    return <Line xscale={this.xscale} yscale={this.yscale} colorscale={this.colorscale} dataSet={pair[1].data} key={pair[0]} colorid={pair[0]} />;
                else if(pair[1].type === 'bar')
                    return <Bar xscale={this.xscale} yscale={this.yscale} colorscale={this.colorscale} dataSet={pair[1].data} key={pair[0]} colorid={pair[0]} />;
            }),
            hoverLine:[]
        };
    }

    onMouseMoveEvent(event) {
        console.log(this.refs.element.parentNode.getBoundingClientRect().left);
        var elX = event.pageX - this.refs.element.parentNode.getBoundingClientRect().left - this.props.xOffset;
        var xVal = this.xscale.invert(elX);
        if(valueIsInDomain(xVal, this.xscale.domain())) {
            this.setState({hoverLine:
                [<Line xscale={this.xscale} yscale={this.yscale} colorscale={this.colorscale} dataSet={[{t: xVal, v: 0}, {t: xVal, v: this.yscale.domain()[1]}]} key={'hoverLine'} colorid={0} />]
            });
        }
    }

    render() {
        return (
            <g className="plot" transform={getPlotTranslation(this.props.xOffset, this.props.yOffset)} ref="element" >
                {this.state.items}
                {this.state.hoverLine}
                <XAxis key="axis" scale={this.xscale} translate={getXScaleTranslation(this.props.height)} />
                <YAxis key="yaxis" scale={this.yscale} />
                <Legend xpos= {this.props.width * .95} ypos={0} colorscale={this.colorscale} items={this.props.dataSets} />
            </g>
        );
    }
}

Plot.propTypes = {
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    xOffset: React.PropTypes.number,
    dataSets: React.PropTypes.object,
    yOffset: React.PropTypes.number,
    mouseEventsRegister: React.PropTypes.func
};

export default Plot;