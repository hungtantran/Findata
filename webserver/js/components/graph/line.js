import React from 'react';
import {line} from 'd3-shape';

function Line(props) {
    var scaledData = line()
        .x((d) => {
            return props.xscale(d.t);
        })
        .y((d) => {
            return props.yscale(d.v);
        })(props.dataSet);

    return <path className="line" d={scaledData} fill="none" strokeWidth="1.5" stroke={props.colorscale(props.colorid) } />;
}

Line.propTypes = {
    xscale: React.PropTypes.func,
    yscale: React.PropTypes.func,
    colorscale: React.PropTypes.func,
    dataSet: React.PropTypes.array,
    colorid: React.PropTypes.number
};

export default Line;