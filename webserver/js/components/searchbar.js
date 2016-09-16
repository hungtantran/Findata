import React from 'react';

class SearchBar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            search: this.props.initialSearch,
            highlightIndex: 0,
            suggestions: {}
        };

        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleKeyDown(event) {
        if (event.key === 'Enter') {
            this.handleSubmit();
        } else if (event.keyCode == '38') {
            // up arrow
            this.setState({highlightIndex: this.state.highlightIndex - 1});
        } else if (event.keyCode == '40') {
            // down arrow
            this.setState({highlightIndex: this.state.highlightIndex + 1});
        }
    }

    handleChange(event) {
        this.setState({
            search: event.target.value,
            highlightIndex: 0,
        });

        // Don't match on empty string
        if (event.target.value) {
            fetch($SCRIPT_ROOT + '/match' + '?match=' + event.target.value, {mode: 'no-cors'})
            .then(function(response) {
                return response.json();
            }).catch(function(ex) {
                console.log('parsing failed', ex);
            }).then((json) => {
                this.setState({ suggestions: json });
            });
        } else {
            this.setState({ suggestions: {} });
        }
    }

    handleSubmit() {
        // If there is selected item, search that, otherwise, use the user's search term
        var searchTerm = this.state.search;
        var searchType = "";
        var searchId = 0;
        var result = this.getSelectedKeyIndex();
        var key = result[0]
        var index = result[1] 
        if (index > 0) {
            searchType = key;
            console.log(this.state.suggestions);
            searchId = this.state.suggestions[key][index - 1].Metadata.Id;
        }

        if (searchTerm.length > 0 || (!searchType && !searchId)) {
            console.log(searchTerm, searchType, searchId);
            this.props.onSearchSubmit({ term: searchTerm, type: searchType, id: searchId});
            this.setState({
                search: this.props.initialSearch,
                suggestions: {}
            });
        }
    }

    getSelectedKeyIndex() {
        var suggestionsLength = 0;
        for (var type in this.state.suggestions) {
            suggestionsLength += this.state.suggestions[type].length;
        }
        // Mod by suggestionsLength + 1 because there is an extra state of non-selected
        var overallIndex = this.state.highlightIndex % (suggestionsLength + 1);
        if (overallIndex < 0) {
            overallIndex += suggestionsLength + 1;
        }

        var key;
        var index;
        for (var type in this.state.suggestions) {
            if (overallIndex > this.state.suggestions[type].length) {
                overallIndex -= this.state.suggestions[type].length;
            } else {
                key = type;
                index = overallIndex;
                break;
            }
        }
        return [key, index];
    }

    render() {
        var result = this.getSelectedKeyIndex();
        var key = result[0]
        var index = result[1]

        var autoSuggestion = [];
        for (var type in this.state.suggestions) {
            // Append the header like "Economics Info", "Metrics", etc...
            autoSuggestion = autoSuggestion.concat(<li className="react-search__menu-header">{type}</li>)
            // Append the actual entries
            autoSuggestion = autoSuggestion.concat(this.state.suggestions[type].map((suggestion, curIndex) => {
                var selected = this.state.highlightIndex != 0 && index == curIndex + 1 && type == key;
                var rowName;
                if (type == "Economics Indicators") {
                    rowName = (
                        <ul className="react-search__menu-item row-result-name multiple-line">
                            <li className="react-search__menu-item row-result-name first-line">{suggestion.Name}</li>
                            <li className="react-search__menu-item row-result-name second-line">{suggestion.Metadata.Ca} - {suggestion.Metadata.Ty}</li>
                        </ul>
                    );
                } else {
                    rowName = suggestion.Name;
                }
                var rowResult = (
                    <ul className="react-search__menu-item row-result">
                        <li className="react-search__menu-item row-result-abbrv">{suggestion.Abbrv}</li>
                        <li className="react-search__menu-item row-result-name">{rowName}</li>
                    </ul>
                );
                if (selected) { 
                    return (
                        <li className="react-search__menu-item selected">{rowResult}</li>
                    );
                } else {
                    return (
                        <li className="react-search__menu-item">{rowResult}</li>
                    );
                }
            }));
        }
        var dropdown = '';
        if (autoSuggestion.length) {
            dropdown =
                <div className="react-search__menu react-search__menu--open">
                    <ul className="react-search__menu-items">
                        {autoSuggestion}
                    </ul>
                </div>;
        }

        return (
            <div className="react-search">            
                <input
                    className="searchBar"
                    type="text"
                    value={this.state.search}
                    placeholder={this.props.placeholderText}
                    onChange={this.handleChange}
                    onKeyDown={this.handleKeyDown}
                />
                {dropdown}
            </div>
        );
    }
}

SearchBar.propTypes = {
    initialSearch: React.PropTypes.string,
    placeholderText: React.PropTypes.string,
    onSearchSubmit: React.PropTypes.func
};
SearchBar.defaultProps = {
    initialSearch: '',
    placeholderText: "Search",
    onSearchSubmit: function (/*submission*/) { }
};

export default SearchBar;
