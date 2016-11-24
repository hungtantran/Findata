import {RECEIVE_SEARCH} from '../actions/searchBarActions';

function Instruments(state={}, action) {
    switch(action.type) {
    case RECEIVE_SEARCH:
        {
            let instruments = {};
            // action.results is a map with:
            // + key: tableCode like "economics_info_431_metrics"
            // + value: object {attribute:attribute, id: attributeId}
            // where attribute is an object
            // {
            //    TableName string
            //    TableCode string
            //    MetricName string
            //    MetricCode string
            // }
            Object.keys(action.results).forEach((key) => {
                if (state[key]) {
                    instruments[key] = Object.assign({}, state[key]);
                } else {
                    instruments[key] = {};
                }

                let pairs = action.results[key];
                pairs.forEach((pair) => {
                    instruments[key][pair.attribute.MetricCode] = pair.id;
                });
            });
            return Object.assign({}, state, instruments);
        }
    default:
        return state;
    }
}

export default Instruments;