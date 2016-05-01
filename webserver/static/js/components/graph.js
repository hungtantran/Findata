import React from 'react'

class Graph extends React.Component {
  render() {
    var contents = "Graph: " + this.props.model.title
    return (
      <div className="graph">{contents}</div>
    )
  }
}

Graph.propTypes = {model: React.PropTypes.object};
Graph.defaultProps = {model: {}};

export default Graph;
