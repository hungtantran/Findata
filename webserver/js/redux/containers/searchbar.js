import {connect} from 'react-redux';
import React from 'react';
import Input from '../components/searchbar/input';
import Suggestions from '../components/searchbar/suggestions';
import {
    searchChanged,
    searchBarSubmit,
    suggestionPressed,
    searchKeyPressed,
    suggestionHovered
} from '../actions/searchBarActions';

class SearchBar extends React.Component {

    render() {
        const {
            searchPlaceholder, 
            currentSearch, 
            suggestions,
            onSearchChange,
            onSearchBarSubmit,
            onSuggestionSubmit,
            onSuggestionHover,
            selectedSuggestion,
            onKeyDown
        } = this.props;

        return (
            <div className="react-search">
                <Input
                    placeholder={searchPlaceholder}
                    currentSearch={currentSearch}
                    onSearchChange={onSearchChange}
                    onSubmit={onSearchBarSubmit}
                    onKeyDown={onKeyDown}
                />
                <Suggestions
                    items={suggestions}
                    onSelected={onSuggestionSubmit}
                    onHovered={onSuggestionHover}
                    selected={selectedSuggestion}
                />
            </div>
        );
    }
}

SearchBar.propTypes = {
    searchPlaceholder: React.PropTypes.string, 
    currentSearch: React.PropTypes.string,
    suggestions: React.PropTypes.object,
    onSearchChange: React.PropTypes.func,
    onSearchBarSubmit: React.PropTypes.func,
    onSuggestionSubmit: React.PropTypes.func,
    onSuggestionHover: React.PropTypes.func,
    selectedSuggestion: React.PropTypes.number,
    onKeyDown: React.PropTypes.func
};

const mapStateToProps = (state) => {
    return {
        searchPlaceholder: state.searchPlaceholder,
        currentSearch: state.currentSearch,
        suggestions: state.suggestions,
        selectedSuggestion: state.selectedSuggestion
    };
};

const mapDispatchToProps = (dispatch) => {
    return {
        onSearchChange: (currentSearch) => dispatch(searchChanged(currentSearch)),
        onSearchBarSubmit: () => dispatch(searchBarSubmit()),
        onSuggestionSubmit: (id) => dispatch(suggestionPressed(id)),
        onSuggestionHover: (id) => dispatch(suggestionHovered(id)),
        onKeyDown: (key) => dispatch(searchKeyPressed(key))
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(SearchBar);