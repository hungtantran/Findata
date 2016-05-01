import React from 'react'

class Table extends React.Component {
  render() {
    var contents = "Table: " + this.props.model.title
    return (
      <div className="table">{contents}</div>
    )
  }
}

Table.propTypes = {model: React.PropTypes.object};
Table.defaultProps = {model: {}};

export default Table;
