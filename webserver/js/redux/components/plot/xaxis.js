import React from 'react';
import {select} from 'd3-selection';
import {axisBottom} from 'd3-axis';

class XAxis extends React.Component {
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
        var axisGenerator = axisBottom(this.props.scale);
        select(this.refs.axis).call(axisGenerator);
    }

    render() {
        return (
            <g className="x axis" ref="axis" transform={this.props.translate} />
        );
    }
}

XAxis.propTypes = {
    scale: React.PropTypes.func,
    translate: React.PropTypes.string
};

export default XAxis;
