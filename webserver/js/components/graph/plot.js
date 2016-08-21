import React from 'react';
import Line from './line';
import Bar from './bar';
import XAxis from './xaxis';
import YAxis from './yaxis';
import {scaleLinear, scaleTime, scaleOrdinal, schemeCategory10} from 'd3-scale';
import {max, min, bisector} from 'd3-array';
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
        this.buildScale = this.buildScales.bind(this);
        this.buildItems = this.buildItems.bind(this);
        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseLeave = this.onMouseLeave.bind(this);

        this.buildScales();
        this.buildItems();
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

    onMouseMove(event) {
        var elX = event.pageX - this.refs.element.parentNode.getBoundingClientRect().left - this.props.xOffset - window.pageXOffset;
        var xVal = this.xscale.invert(elX);
        if(valueIsInDomain(xVal, this.xscale.domain())) {
            var style = {strokeWidth: '1', strokeLinecap: 'round', strokeDasharray: '5,5'};
            var lines = [<Line xscale={this.xscale} yscale={this.yscale} colorscale={this.colorscale} dataSet={[{t: xVal, v: 0}, {t: xVal, v: this.yscale.domain()[1]}]} key={'hoverLinex'} colorid={'0'} style={style} />];
            var dateBisector = bisector(function(d) {
                return new Date(d.t);
            }).right;
            var yVal = Entries(this.props.dataSets).map((pair) => {
                var index = dateBisector(pair[1].data, xVal);
                return pair[1].data[index].v;
            });

            yVal.forEach((val, index) => {
                console.log('Building line with y = ' + val);
                lines.push(<Line xscale={this.xscale} yscale={this.yscale} colorscale={this.colorscale} dataSet={[{t: this.xscale.domain()[0], v: val}, {t: this.xscale.domain()[1], v: val}]} key={`hoverLiney${index}`} colorid={'0'} style={style} />);
            });

            this.setState({hoverLine:lines});
        } else if(this.state.hoverLine.length > 0) {
            this.setState({hoverLine: []});
        }
    }

    onMouseLeave() {
        if(this.state.hoverLine.length > 0) {
            this.setState({hoverLine: []});
        }
    }

    componentDidMount() {
        this.refs.element.parentNode.addEventListener('mousemove', this.onMouseMove);
        this.refs.element.parentNode.addEventListener('mouseleave', this.onMouseLeave);
    }

    render() {
        return (
            <g className="plot" transform={getPlotTranslation(this.props.xOffset, this.props.yOffset)} ref="element" >
                {this.state.items}
                {this.state.hoverLine}
                <XAxis key="axis" scale={this.xscale} translate={getXScaleTranslation(this.props.height)} />
                <YAxis key="yaxis" scale={this.yscale} translate={getYScaleTranslation(this.props.width * .95)} />
                <Legend xpos={this.props.width * .95} ypos={0} colorscale={this.colorscale} items={this.props.dataSets} />
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