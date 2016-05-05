import React from 'react'
import GraphModel from '../../models/graphmodel.json'

class Graph extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        var contents = "Graph: " + JSON.stringify(this.props)
        return (
            <div className="graph">{contents}</div>
        )
    }
}

Graph.propTypes = {
    title: React.PropTypes.string,
    data: React.PropTypes.array
}
Graph.defaultProps = Object.assign({}, GraphModel)

export default Graph;
