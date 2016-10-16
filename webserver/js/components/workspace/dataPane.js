import React from 'react';

function DataPane(props) {
    var groupItems = props.model.map((graph) => {
        return <li className="list-group-item" key={graph.graph.Title}>{graph.graph.Title}</li>;
    });

    return (
    <ul className="list-group">
        {groupItems}
    </ul>
    );
}

export default DataPane;