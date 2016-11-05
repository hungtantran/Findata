import React from 'react';
import {select} from 'd3-selection';
import {axisRight} from 'd3-axis';

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
        var axisGenerator = axisRight(this.props.scale);
        select(this.refs.axis).call(axisGenerator);
    }

    render() {
        return (
            <g className="y axis" ref="axis" transform={this.props.translate} />
        );
    }
}

YAxis.propTypes = {
    scale: React.PropTypes.func,
    translate: React.PropTypes.string
};

export default YAxis;
