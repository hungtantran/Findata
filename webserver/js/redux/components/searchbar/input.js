import React from 'react';

class Input extends React.Component {

    constructor(props) {
        super(props);

        this.handleChange = this.handleChange.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
    }

    handleChange(changeEvent) {
        this.props.onSearchChange(changeEvent.target.value);
    }

    handleKeyDown(keyEvent) {
        if (keyEvent.key === 'Enter')
            this.props.onSubmit();
        else
            this.props.onKeyDown(keyEvent.keyCode);
    }

    render() {
        return (
            <input
                className="searchBar"
                type="text"
                value={this.props.currentSearch}
                placeholder={this.props.placeholder}
                onChange={this.handleChange}
                onKeyDown={this.handleKeyDown}
            />
        );
    }
}

Input.propTypes = {
    placeholder: React.PropTypes.string,
    currentSearch: React.PropTypes.string,
    onSearchChange: React.PropTypes.func,
    onSubmit: React.PropTypes.func,
    onKeyDown: React.PropTypes.func
};

export default Input;