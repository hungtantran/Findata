import {connect} from 'react-redux';
import React from 'react';

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
                    <div title={key}
                    style={{fontSize: 10, overflow: 'hidden', textOverflow: 'ellipsis', width: this.legendWidth, color: item.innerItems[key]}} >
                        {key}
                    </div>
                );
            });
            totalHeight += item.height;
            legendItems.push(
                <div height={heightString} style={{minHeight: heightString, maxHeight: heightString, overflow: 'scroll'}} >
                    {innerItems}
                </div>);
        });

        return (
            <div className='legend' height={totalHeight}>
                {legendItems}
            </div>
        );
    }
}

Legend.propTypes = {
    items: React.PropTypes.array,
};

const mapStateToProps = (state, ownProps) => {

    let graphId = ownProps.id;
    let info = state.elements[graphId];

    let items = [];
    info.plots.forEach((plot, index) => {
        items.push({});
        let plotInfo = state.plots[plot];
        items[index].height = plotInfo.height;
        items[index].innerItems = {};
        state.plots[plot].dataSets.forEach((dataSet) => {
            let name = state.dataSets[dataSet].tableName;
            // Don't concatenate duplicate string when table name equals metric name
            if (name != state.dataSets[dataSet].metricName) {
                name += ' ' + state.dataSets[dataSet].metricName;
            }
            items[index].innerItems[name] = info.colorScale(dataSet);
        });
    });

    return {items};
};

export default connect(
    mapStateToProps
)(Legend);