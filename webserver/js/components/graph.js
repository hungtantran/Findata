import React from 'react'
import GraphModel from '../../models/graphmodel.json'
import GoogleChartLoader from '../googleChartLoader'

class Graph extends React.Component {
    constructor(props) {
        super(props)

        this.draw = this.draw.bind(this)
    }

    componentDidMount() {
        console.log("Graph mounted")
        this.draw() 
    }

    componentDidUpdate() {
        console.log("Graph updating...")  
        this.draw()    
    }

    render() {
        console.log("rendering graph")
        return (
            <div className="graph" ref="graphRef" ></div>
        )
    }

    draw() {
        GoogleChartLoader.load().then(() => {
            if(this.props.data.length === 0) {
                return
            }

            var data = new google.visualization.DataTable();
            data.addColumn('date', 'Date');
            data.addColumn('number', 'Value');

            data.addRows(this.props.data);


            var options = {
              chart: {
                title: this.props.title
              },
              width: 900,
              height: 500,
              hAxis: { format: 'M/d/yy'}
            };

            var chart = new google.charts.Line(this.refs.graphRef);
            chart.draw(data, google.charts.Line.convertOptions(options));
        })
    }
}

Graph.propTypes = {
    title: React.PropTypes.string,
    data: React.PropTypes.array
}
Graph.defaultProps = Object.assign({}, GraphModel)

export default Graph;
