import React from 'react'
import GoogleChartLoader from './googleChartLoader'
import Graph from './graph'

class GraphContainer extends React.Component {

  constructor(props) {
    console.log('constructor');
    super(props);
  }

  componentDidMount() {
    console.log('componentDidMount');
    GoogleChartLoader.load().then(() => {
      console.log('Google loaded')
      Graph.draw(this.refs.graphContainer)
    })
  }

  componentDidUpdate() {
    console.log('componentDidUpdate');
    Graph.draw(this.refs.graphContainer)
  }

  render() {
    console.log('render');
    return (
      <div ref='graphContainer'>Loading graph...</div>
    );
  }
}

GraphContainer.propTypes = {};
GraphContainer.defaultProps = {};

export default GraphContainer;
