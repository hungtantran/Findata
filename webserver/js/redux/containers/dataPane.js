import React from 'react';
import { connect } from 'react-redux';

const DataPane = ({instruments}) => {
    let groupItems = Object.keys(instruments).map((instrument) => {
        return <li className="list-group-item" key={instrument}>{instrument}</li>;
    });

    return (
    <ul className="list-group">
        {groupItems}
    </ul>
    );
};

DataPane.propTypes = {
    instruments: React.PropTypes.object
};

function mapStateToProps(state) {
    return { instruments: state.instruments };
}

export default connect(mapStateToProps)(DataPane);