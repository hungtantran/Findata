import React from 'react';
import { connect } from 'react-redux';

const DataPane = ({tableNameToMetricsMap}) => {
    let groupItems = Object.keys(tableNameToMetricsMap).map((tableName) => {
        let attributes = tableNameToMetricsMap[tableName];
        console.log(attributes);
        // attributeList is the list of attributes for the current table name
        let attributeList = [];
        attributes.forEach((attribute) => {
            attributeList.push(
                <li className='list-group-item' key={attribute.metricName} >
                    {attribute.metricName}
                </li>);
        });
        return (
            <li className='list-group-item' key={tableName} >
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
                        style={{width: '100%'}}>
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
};

DataPane.propTypes = {
    tableNameToMetricsMap: React.PropTypes.object
};

function mapStateToProps(state) {
    let dataSets = state.dataSets;
    var tableNameToMetricsMap = {};
    Object.keys(dataSets).forEach((id) => {
        let dataSet = dataSets[id];
        if (!(dataSet.tableName in tableNameToMetricsMap)) {
            tableNameToMetricsMap[dataSet.tableName] = [];
        }
        tableNameToMetricsMap[dataSet.tableName].push({
            metricCode: dataSet.metricCode,
            metricName: dataSet.metricName,
            tableCode: dataSet.tableCode,
            tableName: dataSet.tableName,
        });
    });
    return { tableNameToMetricsMap: tableNameToMetricsMap };
}

export default connect(mapStateToProps)(DataPane);