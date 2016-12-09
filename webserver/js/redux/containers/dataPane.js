import React from 'react';
import { connect } from 'react-redux';
import {
    filterChanged
} from '../actions/dataPaneActions';
import {startDrag, endDrag} from '../actions/dragDropActions';

class DataPane extends React.Component {
    constructor(props) {
        super(props);

        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(changeEvent) {
        this.props.onFilterChange(changeEvent.target.id, changeEvent.target.value);
    }

    render() {
        let groupItems = Object.keys(this.props.tableCodeToMetricsMap).map((tableCode) => {
            let tableName = this.props.tableCodeToMetricsMap[tableCode]['tableName'];
            let filter = this.props.tableCodeToMetricsMap[tableCode]['filter'];
            let attributes = this.props.tableCodeToMetricsMap[tableCode]['metrics'];
            // attributeList is the list of attributes for the current table name
            let attributeList = [];
            attributeList.push(
                <input
                    id={tableCode}
                    type="text"
                    className="form-control"
                    placeholder="Filter..."
                    onChange={this.handleChange}
                />
            );
            attributes.forEach((attribute) => {
                if (filter !== '' &&
                    attribute.metricName.toLowerCase().indexOf(filter) === -1) {
                    return;
                }
                attributeList.push(
                    <li
                        className='list-group-item'
                        key={attribute.metricName}
                        draggable='true'
                        onDragStart={(ev) => {this.props.onDragStart(attribute.dataId); }}
                        onDragEnd={(ev) => {ev.stopPropagation(); this.props.onDragEnd();}}
                        >
                        {attribute.metricName}
                    </li>);
            });
            return (
                <li className='list-group-item' key={tableCode} >
                    <div className='dropdown'>
                        <button
                            className='btn btn-default dropdown-toggle'
                            title={tableName}
                            type='button'
                            id='dropdownMenu1'
                            data-toggle='dropdown'
                            aria-haspopup='true'
                            aria-expanded='true'
                            style={{width: '100%', overflow: 'hidden', textOverflow: 'ellipsis'}}>
                            {tableName}
                            <span className='caret'></span>
                        </button>
                        <ul
                            className='dropdown-menu'
                            aria-labelledby='dropdownMenu1'
                            style={{width: '110%', maxHeight: '300px', overflowY: 'overlay'}}>
                            {attributeList}
                        </ul>
                    </div>
                </li>);
        });

        return (
            <ul className='list-group'>
                {groupItems}
            </ul>
        );
    }
}

DataPane.propTypes = {
    tableCodeToMetricsMap: React.PropTypes.object,
    onFilterChange: React.PropTypes.func,
};

function mapStateToProps(state) {
    let dataSets = state.dataSets;
    var tableCodeToMetricsMap = {};
    Object.keys(dataSets).forEach((id) => {
        let dataSet = dataSets[id];
        if (!(dataSet.tableCode in tableCodeToMetricsMap)) {
            tableCodeToMetricsMap[dataSet.tableCode] = {};
            tableCodeToMetricsMap[dataSet.tableCode]['tableName'] = dataSet.tableName;
            tableCodeToMetricsMap[dataSet.tableCode]['tableCode'] = dataSet.tableCode;
            tableCodeToMetricsMap[dataSet.tableCode]['filter'] = '';
            tableCodeToMetricsMap[dataSet.tableCode]['metrics'] = [];
        }
        tableCodeToMetricsMap[dataSet.tableCode]['metrics'].push({
            dataId: id,
            metricCode: dataSet.metricCode,
            metricName: dataSet.metricName,
        });
    });

    Object.keys(tableCodeToMetricsMap).forEach((tableCode) => {
        tableCodeToMetricsMap[tableCode]['metrics'].sort(function(metric1, metric2) {
            return metric1.metricName.localeCompare(metric2.metricName);
        });
    });

    let dataPane = state.dataPane;
    Object.keys(dataPane).forEach((tableCode) => {
        if (tableCode in tableCodeToMetricsMap) {
            tableCodeToMetricsMap[tableCode]['filter'] =
                dataPane[tableCode]['filter'].toLowerCase();
        }
    });
    return { tableCodeToMetricsMap: tableCodeToMetricsMap };
}

const mapDispatchToProps = (dispatch) => {
    return {
        onFilterChange: (tableCode, filter) => dispatch(filterChanged(tableCode, filter)),
        onDragStart: (dataSetId) => dispatch(startDrag({source: 'dataPane', dataSetId})),
        onDragEnd: () => dispatch(endDrag())
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(DataPane);