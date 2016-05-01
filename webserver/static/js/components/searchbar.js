import React from 'react'

class SearchBar extends React.Component {

    constructor(props) {
        super(props)
        this.state = {search: this.props.initialSearch}

        this.handleKeyPress = this.handleKeyPress.bind(this)
        this.handleChange = this.handleChange.bind(this)
        this.handleSubmit = this.handleSubmit.bind(this)
    }

    handleKeyPress(event) {
        if(event.key == 'Enter') {
            this.handleSubmit()
        }
    }

    handleChange(event) {
        this.setState({search: event.target.value})
    }

    handleSubmit() {
        this.props.onSearchSubmit({search: this.state.search})
        this.setState({search: this.props.initialSearch})   
    }

    render() {
        return (
            <input
                className="searchBar"
                type="text"
                value={this.state.search}
                placeholder="Whatchu wanna know..."
                onChange={this.handleChange}
                onKeyPress={this.handleKeyPress}
            />
        )
    }
}

SearchBar.propTypes = {
    initialSearch: React.PropTypes.string,
    onSearchSubmit: React.PropTypes.func
}
SearchBar.defaultProps = {
    initialSearch: '',
    onSearchSubmit: function(submission){}
}

export default SearchBar
