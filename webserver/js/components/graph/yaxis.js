import React from 'react';
import {select} from 'd3-selection';
import {axisLeft} from 'd3-axis';

class YAxis extends React.Component {
    constructor(props) {
        super(props);

        this.generateAxis = this.generateAxis.bind(this);
    }

    componentDidMount() {
        this.generateAxis();
    }

    componentDidUpdate() {
        this.generateAxis();
    }

    generateAxis() {
        var axisGenerator = axisLeft(this.props.scale);
        select(this.refs.axis).call(axisGenerator);
    }

    render() {
        return (
            <g className="y axis" ref="axis" />
        );
    }
}

YAxis.propTypes = {
    scale: React.PropTypes.func
};

export default YAxis;
