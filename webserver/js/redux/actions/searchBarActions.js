import {getSelectedKeyIndex} from '../common/utilities';
import {addElement} from './elementActions';
import {addPlots} from './plotActions';
import Guid from 'guid';

export const REQUEST_SUGGESTIONS = 'REQUEST_SUGGESTIONS';
export const RECEIVE_SUGGESTIONS = 'RECEIVE_SUGGESTIONS';
export const REQUEST_SEARCH = 'REQUEST_SEARCH';
export const RECEIVE_SEARCH = 'RECEIVE_SEARCH';
export const CLEAR_SUGGESTIONS = 'CLEAR_SUGGESTIONS';
export const SEARCH_BAR_SUBMIT = 'SEARCH_BAR_SUBMIT';
export const SUGGESTION_PRESSED = 'SUGGESTION_PRESSED';
export const SUGGESTION_HOVERED = 'SUGGESTION_HOVERED';
export const SEARCH_KEY_PRESSED = 'SEARCH_KEY_PRESSED';

function requestSuggestions(currentSearch) {
    return {type: REQUEST_SUGGESTIONS, currentSearch};
}

function clearSuggestions() {
    return {type: CLEAR_SUGGESTIONS};
}

function receiveSuggestions(suggestions) {
    return {type: RECEIVE_SUGGESTIONS, suggestions};
}

export function searchChanged(currentSearch) {
    return dispatch=> {
        if (currentSearch) {
            dispatch(requestSuggestions(currentSearch));
            return fetch($SCRIPT_ROOT + '/match' + '?match=' + currentSearch, {mode: 'no-cors'})
            .then(function(response) {
                return response.json();
            }).catch(function(ex) {
                console.log('parsing failed', ex);
            }).then((json) => {
                dispatch(receiveSuggestions(json));
            });
        } else {
            dispatch(clearSuggestions());
        }
    };
}

function requestSearch(currentSearch) {
    return {type: REQUEST_SEARCH, currentSearch};
}

function receiveSearch(results) {
    return {type: RECEIVE_SEARCH, results};
}

function search(dispatch, getState) {
    const state = getState().searchBar;
    const currentSearch = state.currentSearch;
    const selectedSuggestion = state.selectedSuggestion;
    const suggestions = state.suggestions;
    const [key, index] = getSelectedKeyIndex(suggestions, selectedSuggestion);

    if(!currentSearch && index == 0)
        return;

    let body = {term: currentSearch, action: 'GetGraph'};
    if(index > 0) {
        body.type = String(key);
        body.id = String(suggestions[key][index - 1].Metadata.Id);
    }

    dispatch(requestSearch(currentSearch));

    // TODO change this to GET request
    return fetch($SCRIPT_ROOT + '/search', {
        credentials: 'same-origin',
        mode: 'no-cors',
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
    }).then(function(response) {
        return response.json();
    }).catch(function(ex) {
        console.log('parsing failed', ex);
    }).then((json) => {
        // TODO validate json
        let instruments = getState().instruments;

        let response = {};
        let plotsToAdd = [];
        Object.keys(json).forEach((key) => {
            // don't add instruments we already know about.
            if(instruments[key])
                return;

            let attributes = json[key];
            response[key] = [];
            attributes.forEach((attribute) => {
                let attributeId = Guid.raw();
                response[key].push({name:attribute, id: attributeId});
                if(attribute == 'adj_close' || attribute == 'volume') {
                    let plotId = Guid.raw();
                    plotsToAdd.push({id:plotId, dataSets:[attributeId]});
                }
            });
        });

        // will create data sets and instruments
        if(Object.keys(response).length > 0) {
            let elementGuid = Guid.raw();
            dispatch(addElement(elementGuid));
            dispatch(receiveSearch(response));
            dispatch(addPlots(plotsToAdd, elementGuid));
        }
    });
}

export function searchBarSubmit() {
    return search;
}

export function suggestionPressed() {
    return search;
}

export function suggestionHovered(id) {
    return {type: SUGGESTION_HOVERED, id };
}

export function searchKeyPressed(key) {
    return {type: SEARCH_KEY_PRESSED, key };
}
