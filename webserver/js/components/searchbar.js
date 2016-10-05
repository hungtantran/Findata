import React from 'react';
import MetricTypeToString from './metricType';

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
        this.handleMouseUp = this.handleMouseUp.bind(this);
        this.handleMouseOver = this.handleMouseOver.bind(this);
    }

    handleMouseUp(event) {
        // Only react to left click
        if (event.button == 0) {
            this.handleSubmit();
        }
    }

    handleMouseOver(event) {
        var curTarget = event.currentTarget;
        var curIndex = curTarget.id;
        this.setState({highlightIndex: curIndex});
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
            searchId = this.state.suggestions[key][index - 1].Metadata.Id;
        }

        if (searchTerm.length > 0 || (!searchType && !searchId)) {
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
        var curTotalIndex = 0;
        for (var type in this.state.suggestions) {
            // Append the header like "Economics Info", "Metrics", etc...
            var typeStr = MetricTypeToString(type);
            autoSuggestion = autoSuggestion.concat(<li className="react-search__menu-header">{typeStr}</li>)
            // Append the actual entries
            autoSuggestion = autoSuggestion.concat(this.state.suggestions[type].map((suggestion, curIndex) => {
                curTotalIndex++;
                var selected = this.state.highlightIndex != 0 && index == curIndex + 1 && type == key;
                var rowName;

                // 
                if (type == 2 /* Economics Indicators */) {
                    rowName = (
                        <ul className="react-search__menu-item row-result-name multiple-line">
                            <li className="react-search__menu-item row-result-name first-line">{suggestion.Name}</li>
                            <li className="react-search__menu-item row-result-name second-line">{suggestion.Metadata.Ca} - {suggestion.Metadata.Ty}</li>
                        </ul>
                    );
                } else {
                    rowName = suggestion.Name;
                }

                // Abbreviation first column, name second column
                var rowResult = (
                    <ul className="react-search__menu-item row-result">
                        <li className="react-search__menu-item row-result-abbrv">{suggestion.Abbrv}</li>
                        <li className="react-search__menu-item row-result-name">{rowName}</li>
                    </ul>
                );

                if (selected) { 
                    return (
                        <li id={curTotalIndex} className="react-search__menu-item selected" onMouseMove={this.handleMouseOver}>{rowResult}</li>
                    );
                } else {
                    return (
                        <li id={curTotalIndex} className="react-search__menu-item" onMouseMove={this.handleMouseOver}>{rowResult}</li>
                    );
                }
            }));
        }
        var dropdown = '';
        if (autoSuggestion.length) {
            dropdown =
                <div
                    className="react-search__menu react-search__menu--open"
                    onMouseUp={this.handleMouseUp}>
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
