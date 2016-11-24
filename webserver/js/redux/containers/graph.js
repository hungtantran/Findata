import {connect} from 'react-redux';
import React from 'react';
import { positionPlot } from '../actions/plotActions';
import Plot from './plot';

class Graph extends React.Component {

    constructor(props) {
        super(props);

        this.updatePlotPositions = this.updatePlotPositions.bind(this);
        this.legendWidth = 100;
    }

    updatePlotPositions() {
        const margins = { top: 20, right: 40, bottom: 30, left: 10 };
        const innerHeight = this.props.height - (margins.top + margins.bottom);
        const plotCount = this.props.plots.length;
        const plotHeight = innerHeight / plotCount;

        this.props.plots.forEach((plot, index) => {
            const y = margins.top + plotHeight * index;
            const innerWidth = (this.props.width - (margins.right + margins.left)) - this.legendWidth;
            const position = { width: innerWidth, height: plotHeight, x: margins.left, y};
            this.props.positionPlot(plot, position);
        });
    }

    shouldComponentUpdate(nextProps) {
        if(this.props.plots.length != nextProps.plots.length)
            return true;

        if(this.props.width != nextProps.width || this.props.height != nextProps.height)
            return true;
        
        for(let i = 0; i < this.props.plots.length; i++) {
            if(this.props.plots[i] != nextProps.plots[i])
                return true;
        }

        return false;
    }

    componentDidMount() {
        this.updatePlotPositions();
    }

    componentDidUpdate() {
        this.updatePlotPositions();
    }

    render() {
        let plotsToRender = this.props.plots.map((plot) => {
            return <Plot id={plot} key={plot} />;
        });

        let legendItems = [];
        Object.keys(this.props.items).forEach((key) => {
            let dataSet = this.props.items[key];
            legendItems.push(
                <div
                    title={key}
                    style={{overflow: 'hidden', textOverflow: 'ellipsis', width: this.legendWidth, color: this.props.items[key]}}
                >
                    {key}
                </div>);
        });

        return (
            <div style={{display: 'flex'}} width={this.props.width}>
                <svg className='graph' width={this.props.width - this.legendWidth} height={this.props.height} >
                    {plotsToRender}
                </svg>
                <div className='legend'>
                    {legendItems}
                </div>
            </div>
        );
    }
}

Graph.propTypes = {
    plots: React.PropTypes.array,
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    positionPlot: React.PropTypes.func,
    // Map between legend name and color scale
    items: React.PropTypes.object
};

const mapStateToProps = (state, ownProps) => {
    var grid = $('.grid-stack').data('gridstack');
    var cellWidth = grid ? grid.cellWidth() : 20;
    var cellHeight = grid ? grid.cellHeight() : 20;

    let graphId = ownProps.id;
    let info = state.elements[graphId];

    let width = info.width ? info.width * cellWidth - 10 : 0;
    let height = info.height ? info.height * cellHeight - 10 : 0;

    let items = {};
    info.plots.forEach((plot) => {
        state.plots[plot].dataSets.forEach((dataSet) => {
            let name = state.dataSets[dataSet].tableName;
            // Don't concatenate duplicate string when table name equals metric name
            if (name != state.dataSets[dataSet].metricName) {
                name += ' ' + state.dataSets[dataSet].metricName;
            }
            items[name] = info.colorScale(dataSet);
        });
    });

    return {width, height, plots: info.plots, items};
};

const mapDispatchToProps = (dispatch) => {
    return {
        positionPlot: (plot, position) => dispatch(positionPlot(plot, position))
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Graph);