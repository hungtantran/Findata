import {connect} from 'react-redux';
import React from 'react';
import {removeDataSetFromPlot} from '../actions/plotActions';
import {startDrag, endDrag} from '../actions/dragDropActions';

class Legend extends React.Component {

    constructor(props) {
        super(props);

        this.legendWidth = 100;
    }

    render() {

        let heightString = (100/this.props.items.length) + '%';
        let totalHeight = 0;
        let legendItems = [];
        this.props.items.forEach((item) => {
            let innerItems = Object.keys(item.innerItems).map((key) => {
                return (
                    <div
                    className='legendItem' 
                    title={key}
                    draggable='true'
                    onDragEnd={(ev) => {
                        ev.stopPropagation();
                        this.props.onDragEnd();
                    }}
                    onDragStart={(ev) => {
                        ev.stopPropagation();
                        this.props.onDragStart(
                            {source: 'legend', dataSetId: item.innerItems[key].id, plotId: item.id, control: ev.ctrlKey || ev.metaKey}
                            );
                    }}
                    style={{fontSize: 10, overflow: 'hidden', textOverflow: 'ellipsis', width: this.legendWidth, color: item.innerItems[key].color}} >
                        {key}
                    </div>
                );
            });
            totalHeight += item.height;
            legendItems.push(
                <div height={heightString} style={{minHeight: heightString, maxHeight: heightString, overflowY: 'auto', overflowX: 'hidden', textOverflow: 'ellipsis'}} >
                    {innerItems}
                </div>);
        });

        return (
            <div className='legend' height={totalHeight} style={{minHeight: totalHeight, maxHeight: totalHeight}}>
                {legendItems}
            </div>
        );
    }
}

Legend.propTypes = {
    items: React.PropTypes.array,
    onDragEnd: React.PropTypes.func,
    onDragStart: React.PropTypes.func
};

const mapStateToProps = (state, ownProps) => {

    let graphId = ownProps.id;
    let info = state.elements[graphId];

    let items = [];
    info.plots.forEach((plot, index) => {
        items.push({});
        let plotInfo = state.plots[plot];
        items[index].height = plotInfo.height;
        items[index].id = plot;
        items[index].innerItems = {};
        state.plots[plot].dataSets.forEach((dataSet) => {
            let name = state.dataSets[dataSet].tableName;
            // Don't concatenate duplicate string when table name equals metric name
            if (name != state.dataSets[dataSet].metricName) {
                name += ' ' + state.dataSets[dataSet].metricName;
            }
            items[index].innerItems[name] = {color: info.colorScale(dataSet), id: dataSet};
        });
    });

    return {items};
};

const mapDispatchToProps = (dispatch, ownProps) => {
    return {
        onDragEnd: () => dispatch(endDrag()),
        onDragStart: (info) => dispatch(startDrag(info))
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Legend);