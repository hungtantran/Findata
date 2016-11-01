import {connect} from 'react-redux';
import React from 'react';
import { positionPlot } from '../actions/plotActions';
import Plot from './plot';

class Graph extends React.Component {

    constructor(props) {
        super(props);

        this.updatePlotPositions = this.updatePlotPositions.bind(this);
    }

    updatePlotPositions() {
        const margins = { top: 20, right: 40, bottom: 30, left: 10 };
        const innerHeight = this.props.height - (margins.top + margins.bottom);
        const plotCount = this.props.plots.length;
        const plotHeight = innerHeight / plotCount;

        this.props.plots.forEach((plot, index) => {
            const y = margins.top + plotHeight * index;
            const innerWidth = this.props.width - (margins.right + margins.left);
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

        return (
            <svg className="graph" width={this.props.width} height={this.props.height} >
                {plotsToRender}
            </svg>
        );
    }
}

Graph.propTypes = {
    plots: React.PropTypes.array,
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    positionPlot: React.PropTypes.func
};

const mapStateToProps = (state, ownProps) => {
    var grid = $('.grid-stack').data('gridstack');
    var cellWidth = grid ? grid.cellWidth() : 20;
    var cellHeight = grid ? grid.cellHeight() : 20;

    let graphId = ownProps.id;
    let info = state.elements[graphId];

    let width = info.width ? info.width * cellWidth - 10 : 0;
    let height = info.height ? info.height * cellHeight - 10 : 0;

    return {width, height, plots: info.plots};
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