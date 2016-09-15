import React from 'react';
import {line} from 'd3-shape';

function Line(props) {
    var scaledData = line()
        .x((d) => {
            return props.xscale(new Date(d.T));
        })
        .y((d) => {
            return props.yscale(d.V);
        })(props.dataSet);

    props.style.className = 'line';
    props.style.d = scaledData;
    props.style.stroke = props.colorscale(props.colorid);
    props.style.fill = 'none';

    return <path {...props.style} />;
}

Line.defaultProps = {
    style: {strokeWidth: '1.5'}
};

Line.propTypes = {
    xscale: React.PropTypes.func,
    yscale: React.PropTypes.func,
    colorscale: React.PropTypes.func,
    dataSet: React.PropTypes.array,
    colorid: React.PropTypes.string,
    style: React.PropTypes.object
};

export default Line;