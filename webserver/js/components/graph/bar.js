import React from 'react';
import {rect} from 'd3-shape';

function Bar(props) {
    var width = (props.xscale.range()[1] - props.xscale.range()[0])/props.dataSet.length;

    var bars = props.dataSet.map(function(item, index) {
        return <rect x={props.xscale(new Date(item.T))} y={props.yscale(item.V)} height={props.yscale(0) - props.yscale(item.V)} width={width} key={index} fill={props.colorscale(props.colorid) }/>;
    });

    return <g>
        {bars}
    </g>;
}

Bar.propTypes = {
    xscale: React.PropTypes.func,
    yscale: React.PropTypes.func,
    colorscale: React.PropTypes.func,
    dataSet: React.PropTypes.array,
    colorid: React.PropTypes.string
};

export default Bar;