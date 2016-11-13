import {connect} from 'react-redux';
import React from 'react';
import Line from '../components/plot/line';

class DataSet extends React.Component {
    constructor(props) {
        super(props);
    }

    // componentDidMount() {
    //     let {dispatch, dataSetsIds} = this.props;
    //     dataSetsIds.forEach((id) => {
    //         dispatch(fetchDataSetIfNeeded(id));
    //     });
    // }

    // componentWillReceiveProps(nextProps) {
    //     if (nextProps.plotId !== this.props.plotId) {
    //         let {dispatch, dataSetsIds} = this.props;
    //         dataSetsIds.forEach((id) => {
    //             dispatch(fetchDataSetIfNeeded(id));
    //         });
    //     }
    // }

    render() {
        return <Line data={this.props.data} yscale={this.props.yscale} xscale={this.props.xscale} />;
    }
}

DataSet.propTypes = {
    data: React.PropTypes.array,
    xscale: React.PropTypes.func,
    yscale: React.PropTypes.func
};

const mapStateToProps = (state, ownProps) => {

    let data = state.dataSets[ownProps.id].data;
    let {xscale, yscale} = ownProps;

    return {data, xscale, yscale};
};

export default connect(
    mapStateToProps
)(DataSet);