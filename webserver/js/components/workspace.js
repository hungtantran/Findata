import React from 'react'
import SearchBar from './searchbar'
import Graph from './graph'
import Table from './table'
import jQuery from 'jquery'
import TableModel from '../../models/tablemodel.json'
import GraphModel from '../../models/graphmodel.json'

class Workspace extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            graphModel: this.props.initialGraphModel,
            tableModel: this.props.initialTableModel
        }

        this.handleSearchSubmit = this.handleSearchSubmit.bind(this)
        this.loadModelsFromJSON = this.loadModelsFromJSON.bind(this)
    }

    loadModelsFromJSON(data) {
        this.setState({
            graphModel: data.graphModel,
            tableModel: data.tableModel
        })
    }

    handleSearchSubmit(submission) {
        var url = this.props.seearchUrlRoot
        jQuery.getJSON(url, {search: submission.search}, this.loadModelsFromJSON)
    }

    render() {
        return(
            <div className="workspace">
                <SearchBar onSearchSubmit={this.handleSearchSubmit} />
                <Graph {...this.state.graphModel} />
                <Table {...this.state.tableModel} />
            </div>
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
