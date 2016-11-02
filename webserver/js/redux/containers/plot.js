import {connect} from 'react-redux';
import React from 'react';
import {fetchDataSetIfNeeded} from '../actions/dataSetActions';

class Plot extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        let {dispatch, dataSetsIds} = this.props;
        dataSetsIds.forEach((id) => {
            dispatch(fetchDataSetIfNeeded(id));
        });
    }

    // componentWillReceiveProps(nextProps) {
    //     if (nextProps.plotId !== this.props.plotId) {
    //         let {dispatch, dataSetsIds} = this.props;
    //         dataSetsIds.forEach((id) => {
    //             dispatch(fetchDataSetIfNeeded(id));
    //         });
    //     }
    // }

    render() {
        return <g/>;
    }
}

Plot.propTypes = {
    dataSetsIds: React.PropTypes.array, 
    dispatch: React.PropTypes.func
};

const mapStateToProps = (state, ownProps) => {
    return {dataSetsIds: state.plots[ownProps.id].dataSets};
};

export default connect(
    mapStateToProps
)(Plot);