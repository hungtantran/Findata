import React from 'react'
import {TableModel} from '../models/datamodels'

class Table extends React.Component {
    constructor(props) {
        super(props)

        this.generateHeaders = this.generateHeaders.bind(this)
        this.generateRows = this.generateRows.bind(this)
    }

    generateHeaders() {
        return (<th>{this.props.model.title}</th>)
    }

    generateRows() {
        return (
            this.props.model.data.map(function(item){
                return (
                    <tr>
                        <td>{item[0]}</td>
                        <td>{item[1]}</td>
                    </tr>
                )
            })
        )
    }

    render() {
        return (
            <table className="table">
                {this.generateHeaders()}
                {this.generateRows()}
            </table>
        )
    }
}

Table.propTypes = {model: React.PropTypes.object};
Table.defaultProps = {model: new TableModel()};

export default Table;
