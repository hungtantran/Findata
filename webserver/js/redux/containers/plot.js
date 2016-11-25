import {connect} from 'react-redux';
import React from 'react';
import {fetchDataSetIfNeeded} from '../actions/dataSetActions';
import {addDataSetToPlot} from '../actions/plotActions';
import PlotDisplay from '../components/plot/plotDisplay';

class Plot extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        let {dispatch, dataSets} = this.props;
        dataSets.forEach((id) => {
            dispatch(fetchDataSetIfNeeded(id));
        });
    }

    // componentWillReceiveProps(nextProps) {
    //     if (nextProps.plotId !== this.props.plotId) {
    //         let {dispatch, dataSetsIds} = this.props;
    //         dataSetsIds.forEach((id) => {
    //             dispatch(fetchDataSetIfNeeded(id));
    //         });
    //     }
    // }

    render() {
        if(this.props.dataSets.length == 0)
            return (
                <text>
                    {'Loading...'}
                </text>
                );
        else
            return <PlotDisplay {...this.props} />;
    }
}

Plot.propTypes = {
    dataSets: React.PropTypes.array,
    range: React.PropTypes.array,
    domain: React.PropTypes.array,
    dispatch: React.PropTypes.func,
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    x: React.PropTypes.number,
    y: React.PropTypes.number,
    colorScale: React.PropTypes.func
};

const mapStateToProps = (state, ownProps) => {

    Date.MIN_VALUE = new Date(-8640000000000000);
    Date.MAX_VALUE = new Date(8640000000000000);
    let xMin = Date.MAX_VALUE, yMin = Infinity;
    let xMax = Date.MIN_VALUE, yMax = -Infinity;

    let plot = state.plots[ownProps.id];
    let dataSetIds = plot.dataSets;
    dataSetIds.forEach((dataSetId) => {
        let [dataYMin, dataYMax] = state.dataSets[dataSetId].range;
        if(dataYMin < yMin)
            yMin = dataYMin;
        if(dataYMax > yMax)
            yMax = dataYMax;
    });

    let parentId = plot.parent;
    let plotsInSameParent = state.elements[parentId].plots;
    plotsInSameParent.forEach((plotId) => {
        let plotsDataSets = state.plots[plotId].dataSets;
        plotsDataSets.forEach((dataSetId) => {
            let [dataXMin, dataXMax] = state.dataSets[dataSetId].domain;
            if(dataXMin < xMin)
                xMin = dataXMin;
            if(dataXMax > xMax)
                xMax = dataXMax;
        });
    });

    let {x, y, width, height } = plot;

    return {dataSets: dataSetIds, domain: [xMin, xMax], range: [yMin, yMax], x, y, width, height, colorScale: state.elements[parentId].colorScale};
};

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        onDragEnd: (dataSetId) => dispatch(addDataSetToPlot(dataSetId, ownProps.id)),
        dispatch
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Plot);