import React from 'react';

class SearchBar extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            search: this.props.initialSearch,
            suggestions: []
        };

        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleKeyPress(event) {
        if (event.key === 'Enter') {
            this.handleSubmit();
        }
    }

    handleChange(event) {
        this.setState({ search: event.target.value });

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
        this.props.onSearchSubmit({ search: this.state.search });
        this.setState({
            search: this.props.initialSearch,
            suggestions: []
        });
    }

    render() {
        var auto_suggestion = this.state.suggestions.map((suggestion) => {
            return <li className="react-search__menu-item"><a>{suggestion}</a></li>
        });
        var dropdown = '';
        if (auto_suggestion.length) {
            dropdown =
                <div className="react-search__menu react-search__menu--open">
                    <ul className="react-search__menu-items">
                        {auto_suggestion}
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
                    onKeyPress={this.handleKeyPress}
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
