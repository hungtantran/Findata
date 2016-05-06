import React from 'react'
import SearchBar from './searchbar'
import Graph from './graph'
import Table from './table'
import jQuery from 'jquery'
import TableModel from '../../models/tablemodel.json'
import GraphModel from '../../models/graphmodel.json'
import GoogleChartLoader from '../googleChartLoader'

class Workspace extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            graphModel: this.props.initialGraphModel,
            tableModel: this.props.initialTableModel,
            googleChartsLoaded: false
        }

        this.handleSearchSubmit = this.handleSearchSubmit.bind(this)
        this.loadModelsFromJSON = this.loadModelsFromJSON.bind(this)
    }

    componentDidMount() {
        GoogleChartLoader.load().then(() => {
            this.setState({googleChartsLoaded: true})
        })
    }

    componentDidUpdate() {
        console.log("workspace updating...")
    }

    render() {
        console.log("Rendering workspace...")
        var components = [<SearchBar onSearchSubmit={this.handleSearchSubmit} />]

        if(this.state.googleChartsLoaded === true && this.state.graphModel.data.length > 0) {
            console.log("Adding graph")
            components.push(<Graph {...this.state.graphModel} />)
        }

        return(
            <div className="workspace">
                {components}
            </div>
        )
    }

    loadModelsFromJSON(data) {
        data.graphModel.data = data.graphModel.data.map(function(item){
            return [new Date(item[0].replace(/-/g, "/")), item[1]]
        })

        console.log("Setting models on state...")
        this.setState({
            graphModel: data.graphModel,
            tableModel: data.tableModel
        })
    }

    handleSearchSubmit(submission) {
        jQuery.getJSON(
            this.props.seearchUrlRoot,
            {search: submission.search},
            this.loadModelsFromJSON
        )
    }
}

Workspace.propTypes = {
    seearchUrlRoot: React.PropTypes.string,
    initialGraphModel: React.PropTypes.object,
    initialTableModel: React.PropTypes.object
}
Workspace.defaultProps = {
    seearchUrlRoot: $SCRIPT_ROOT + '/search',
    initialGraphModel: Object.assign({}, GraphModel),
    initialTableModel: Object.assign({}, TableModel)
}

export default Workspace
