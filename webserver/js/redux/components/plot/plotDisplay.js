import React from 'react';
import DataSet from '../../containers/dataSet';
import XAxis from './xaxis';
import YAxis from './yaxis';
import {scaleLinear, scaleTime} from 'd3-scale';

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
        this.buildItems = this.buildItems.bind(this);
    }

    buildItems(dataSets, xscale, yscale) {
        return Array.from(dataSets, (dataSet) => {
            return <DataSet key={dataSet} id={dataSet} xscale={xscale} yscale={yscale} />;
        });
    }

    render() {
        if(this.props.width == 0 || this.props.height == 0)
            return <g/>;

        let xscale = scaleTime()
            .domain(this.props.domain)
            .range([0, this.props.width * .95]);
        let yscale = scaleLinear()
            .domain(this.props.range)
            .range([this.props.height, 0]);
        let dataSets = this.buildItems(this.props.dataSets, xscale, yscale);
        return (
            <g className="plot" transform={getPlotTranslation(this.props.x, this.props.y)} ref="element" >
                <clipPath id='clip'>
                    <rect width={this.props.width * .95} height={this.props.height} />
                </clipPath>
                <g ref="items" clipPath='url(#clip)' >
                    {dataSets}
                </g>
                <XAxis scale={xscale} translate={getXScaleTranslation(this.props.height)} />
                <YAxis scale={yscale} translate={getYScaleTranslation(this.props.width * .95)} />
            </g>
        );
    }
}

PlotDisplay.propTypes = {
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    x: React.PropTypes.number,
    y: React.PropTypes.number,
    dataSets: React.PropTypes.array,
    domain: React.PropTypes.array,
    range: React.PropTypes.array
};

export default PlotDisplay;