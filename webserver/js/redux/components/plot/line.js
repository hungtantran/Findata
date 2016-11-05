import React from 'react';
import {line} from 'd3-shape';

function Line(props) {
    var scaledData = line()
        .x((d) => {
            return props.xscale(d.t);
        })
        .y((d) => {
            return props.yscale(d.v);
        })(props.data);


    props.style.className = 'line';
    props.style.stroke = 'blue';
    props.style.d = scaledData;
    props.style.fill = 'none';
    return <path {...props.style} />;
}

Line.defaultProps = {
    style: {strokeWidth: '1.5'}
};

Line.propTypes = {
    xscale: React.PropTypes.func,
    yscale: React.PropTypes.func,
    data: React.PropTypes.array,
    style: React.PropTypes.object
};

export default Line;