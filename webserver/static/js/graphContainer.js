import React from 'react'
import GoogleChartLoader from './googleChartLoader'

class GraphContainer extends React.Component {

  constructor(props) {
    super(props);
    this.props.graph = props.graph;
  }

  componentDidMount() {
    console.log("Graph container mounted!")
    GoogleChartLoader.load().then(() => {
      this.props.graph.draw(this.refs.graphContainer)
    })
  }

  componentDidUpdate() {
    //this.props.graph.draw(this.refs.graphContainer)
  }

  render() {
    console.log("Graph container rendering!")
    return (
      <div ref='graphContainer'>Loading graph...</div>
    );
  }
}

GraphContainer.propTypes = {};
GraphContainer.defaultProps = {};

export default GraphContainer;
