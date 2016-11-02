export const REQUEST_DATA_SET = 'REQUEST_DATA_SET';
export const RECIEVE_DATA_SET = 'RECIEVE_DATA_SET';

function requestDataSet(id) {
    return {type: REQUEST_DATA_SET, id};
}

function recieveDataSet(id, data) {
    return {type: RECIEVE_DATA_SET, id, data};
} 

function fetchDataSet(id) {
    return (dispatch, getState) => {
        let state = getState();
        dispatch(requestDataSet(id));
        let {name, tableName} = state.dataSets[id];
        fetch($SCRIPT_ROOT + '/search', {
            mode: 'no-cors',
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'GetData',
                metricName: name,
                tableName: tableName,
            })
        }).then(function(response) {
            return response.json();
        }).catch(function(ex) {
            console.log('parsing failed', ex);
        }).then((json) => {
            dispatch(recieveDataSet(id, json));
        });
    };
}

function shouldFetchDataSet(state, id) {
    return (state.dataSets[id].data.length == 0 && !state.dataSets[id].isFetching)
}

export function fetchDataSetIfNeeded(id) {
    return (dispatch, getState) => {
        let state = getState();
        if (shouldFetchDataSet(state, id))
            return dispatch(fetchDataSet(id));
    };
}