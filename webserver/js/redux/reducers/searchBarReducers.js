import * as Actions from '../actions/searchBarActions';

const initialState = {
    searchPlaceholder: 'Search...',
    currentSearch: '',
    suggestions: {},
    selectedSuggestion: 0,
    isFetchingSuggestions: false,
    instruments: {}
};

function SearchBar(state = initialState, action) {
    switch(action.type) {
    case Actions.REQUEST_SUGGESTIONS:
        return Object.assign({}, state, {
            currentSearch: action.currentSearch,
            selectedSuggestion: 0,
            isFetchingSuggestions: true
        });
    case Actions.RECEIVE_SUGGESTIONS:
        return Object.assign({}, state, {
            selectedSuggestion: 0,
            suggestions: action.suggestions,
            isFetchingSuggestions: false
        });
    case Actions.CLEAR_SUGGESTIONS:
        return Object.assign({}, state, {
            currentSearch: '',
            selectedSuggestion: 0,
            suggestions: {}
        });
    case Actions.REQUEST_SEARCH:
        return Object.assign({}, state, {
            currentSearch: '',
            selectedSuggestion: 0,
            suggestions: {}
        });
    case Actions.SUGGESTION_HOVERED:
        return Object.assign({}, state, {
            selectedSuggestion: action.id,
        });
    case Actions.SEARCH_KEY_PRESSED:
        {
            let currentSuggestion = state.selectedSuggestion;
            if(action.key == '38') {
                return Object.assign({}, state, {
                    selectedSuggestion: currentSuggestion - 1,
                });
            } else if(action.key == '40') {
                return Object.assign({}, state, {
                    selectedSuggestion: currentSuggestion + 1,
                });
            }
            return state;
        }
    default:
        return state;
    }
}

export default SearchBar;