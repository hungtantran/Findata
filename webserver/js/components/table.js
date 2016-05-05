import React from 'react'
import TableModel from '../../models/tablemodel.json'

class Table extends React.Component {
    constructor(props) {
        super(props)
        console.log(props)

        this.generateHeaders = this.generateHeaders.bind(this)
        this.generateRows = this.generateRows.bind(this)
    }

    generateHeaders() {
        return (<th>{this.props.title}</th>)
    }

    generateRows() {
        return (
            this.props.data.map(function(item){
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

Table.propTypes = {
    title: React.PropTypes.string,
    data: React.PropTypes.array
}
Table.defaultProps = Object.assign({}, TableModel)

export default Table;
