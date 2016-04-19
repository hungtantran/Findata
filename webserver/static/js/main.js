$(function(){
  'use strict';

  var myLayout = new GoldenLayout({
    content: [{
      type: 'row',
      content: [{
        type: 'react-component',
        component: 'chart-test',
        props: { label: 'A' },
        title: 'A title'
      }, {
        type: 'column',
        content: [{
          type: 'react-component',
          component: 'chart-test',
          props: { label: 'B' }
        }, {
          type: 'react-component',
          component: 'chart-test',
          props: { label: 'C' }
        }]
      }]
    }]
  });

  var TestComponent = React.createClass({
    displayName: 'TestComponent',

    render: function render() {
      return React.createElement(
        'h1',
        {className: 'testComponent'},
        this.props.label
      );
    }
  });

  var d3Chart = {};

  d3Chart.create = function(el, props, state) {
    var svg = d3.select(el).append('svg')
        .attr('class', 'd3')
        .attr('width', props.width)
        .attr('height', props.height);

    svg.append('g')
        .attr('class', 'd3-points');

    this.update(el, state);
  };

  d3Chart.update = function(el, state) {
    // Re-compute the scales, and render the data points
    var scales = this._scales(el, state.domain);
    this._drawPoints(el, scales, state.data);
  };

  d3Chart._scales = function(el, domain) {
    if (!domain) {
      return null;
    }

    var width = el.offsetWidth;
    var height = el.offsetHeight;

    var x = d3.scale.linear()
      .range([0, width])
      .domain(domain.x);

    var y = d3.scale.linear()
      .range([height, 0])
      .domain(domain.y);

    var z = d3.scale.linear()
      .range([5, 20])
      .domain([1, 10]);

    return {x: x, y: y, z: z};
  };

  d3Chart.destroy = function(el) {
    // Any clean-up would go here
    // in this example there is nothing to do
  };

  d3Chart._drawPoints = function(el, scales, data) {
    var g = d3.select(el).selectAll('.d3-points');

    var point = g.selectAll('.d3-point')
      .data(data, function(d) { return d.id; });

    // ENTER
    point.enter().append('circle')
        .attr('class', 'd3-point');

    // ENTER & UPDATE
    point.attr('cx', function(d) { return scales.x(d.x); })
        .attr('cy', function(d) { return scales.y(d.y); })
        .attr('r', function(d) { return scales.z(d.z); });

    // EXIT
    point.exit()
        .remove();
  };

  var Chart = React.createClass({
    propTypes: {
      data: React.PropTypes.array,
      domain: React.PropTypes.object
    },

    componentDidMount: function() {
      var el = this.refs.chart;
      d3Chart.create(el, {
        width: '100%',
        height: '300px'
      }, this.getChartState());
    },

    componentDidUpdate: function() {
      var el = this.refs.chart;
      d3Chart.update(el, this.getChartState());
    },

    getChartState: function() {
      return {
        data: this.props.data,
        domain: this.props.domain
      };
    },

    componentWillUnmount: function() {
      var el = this.refs.chart;
      d3Chart.destroy(el);
    },

    render: function() {
      return (
        <div ref = "chart" className="Chart"></div>
      );
    }
  });

  var sampleData = [
    {id: '5fbmzmtc', x: 7, y: 41, z: 6},
    {id: 's4f8phwm', x: 11, y: 45, z: 9},
    {id: '1', x: 20, y: 45, z: 9},
    {id: '2', x: 8, y: 45, z: 9},
    {id: '3', x: 27, y: 45, z: 9},
    {id: '4', x: 23, y: 45, z: 9},
    {id: '5', x: 2, y: 45, z: 9},
    {id: '6', x: 16, y: 45, z: 9},
    {id: '7', x: 19, y: 45, z: 9},
    {id: '8', x: 7, y: 45, z: 9},
  ];

  var App = React.createClass({
    getInitialState: function() {
      return {
        data: sampleData,
        domain: {x: [0, 30], y: [0, 100]}
      };
    },

    render: function() {
      return (
        <div className="App">
          <Chart
            data={this.state.data}
            domain={this.state.domain} />
        </div>
      );
    }
  });

  myLayout.registerComponent('test-component', TestComponent);
  myLayout.registerComponent('chart-test', App)

  //Once all components are registered, call
  myLayout.init();
});
