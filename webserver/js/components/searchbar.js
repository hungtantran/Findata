import React from 'react';

class SearchBar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            search: this.props.initialSearch,
            highlightIndex: 0,
            suggestions: []
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
            this.setState({ suggestions: [] });
        }
    }

    handleSubmit() {
        // If there is selected item, search that, otherwise, use the user's search term
        var searchTerm = this.state.search;
        var selectedIndex = this.getSelectedIndex(); 
        if (selectedIndex > 0) {
            searchTerm = this.state.suggestions[selectedIndex - 1];
        }

        if (searchTerm.length > 0) {
            this.props.onSearchSubmit({ search: searchTerm });
            this.setState({
                search: this.props.initialSearch,
                suggestions: []
            });
        }
    }

    getSelectedIndex() {
        var suggestionsLength = this.state.suggestions.length;
        // Mod by suggestionsLength + 1 because there is an extra state of non-selected
        var index = this.state.highlightIndex % (suggestionsLength + 1);
        if (index < 0) {
            index += suggestionsLength + 1;
        }
        return index;
    }

    render() {
        var index = this.getSelectedIndex();
        var autoSuggestion = this.state.suggestions.map((suggestion, curIndex) => {
            var selected = this.state.highlightIndex != 0 && index == curIndex + 1;
            if (selected) { 
                return <li className="react-search__menu-item selected">{suggestion}</li>
            } else {
                return <li className="react-search__menu-item">{suggestion}</li>
            }
        });
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
    placeholderText: 'Whatchu wanna know...',
    onSearchSubmit: function (/*submission*/) { }
};

export default SearchBar;
