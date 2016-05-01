import React from 'react'
import {GraphModel} from '../models/datamodels'

class Graph extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        var contents = "Graph: " + JSON.stringify(this.props.model)
        return (
            <div className="graph">{contents}</div>
        )
    }
}

Graph.propTypes = {model: React.PropTypes.object};
Graph.defaultProps = {model: new GraphModel()};

export default Graph;
