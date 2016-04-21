import React from 'react'

class Graph extends React.Component {

  constructor(props) {
    console.log('constructor');
    super(props);
  }

  componentDidMount() {
    console.log('componentDidMount');
  }

  componentDidUpdate() {
    console.log('componentDidUpdate');
  }

  render() {
    console.log('render');
    return (
      <div ref='graphContainer'>This is going to be a graph</div>
    );
  }
}

Graph.propTypes = {};
Graph.defaultProps = {};

export default Graph;