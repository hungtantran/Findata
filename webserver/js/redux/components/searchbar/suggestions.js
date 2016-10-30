import React from 'react';
import MetricTypeToString from '../../common/metricType';
import {getSelectedKeyIndex} from '../../common/utilities';

class Suggestions extends React.Component {

    constructor(props) {
        super(props);

        this.handleMouseOver = this.handleMouseOver.bind(this);
        this.handleMouseUp = this.handleMouseUp.bind(this);
    }

    handleMouseUp(event) {
        // Only react to left click
        if (event.button == 0) {
            this.props.onSelected();
        }
    }

    handleMouseOver(event) {
        var curTarget = event.currentTarget;
        var curIndex = Number(curTarget.id);
        this.props.onHovered(curIndex);
    }

    render() {
        let result = getSelectedKeyIndex(this.props.items, this.props.selected);
        let key = result[0];
        let index = result[1];

        let autoSuggestion = [];
        let curTotalIndex = 0;
        for (let type in this.props.items) {
            // Append the header like "Economics Info", "Metrics", etc...
            let typeStr = MetricTypeToString(type);
            autoSuggestion = autoSuggestion.concat(<li key={Math.random()} className="react-search__menu-header">{typeStr}</li>);
            // Append the actual entries
            autoSuggestion = autoSuggestion.concat(this.props.items[type].map((suggestion, curIndex) => {
                curTotalIndex++;
                let selected = this.props.selected != 0 && index == curIndex + 1 && type == key;
                let rowName;

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
                let rowResult = (
                    <ul className="react-search__menu-item row-result">
                        <li className="react-search__menu-item row-result-abbrv">{suggestion.Abbrv}</li>
                        <li className="react-search__menu-item row-result-name">{rowName}</li>
                    </ul>
                );

                if (selected) { 
                    return (
                        <li key={Math.random()} id={curTotalIndex} className="react-search__menu-item selected" onMouseMove={this.handleMouseOver}>{rowResult}</li>
                    );
                } else {
                    return (
                        <li key={Math.random()} id={curTotalIndex} className="react-search__menu-item" onMouseMove={this.handleMouseOver}>{rowResult}</li>
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
            <div>
                {dropdown}
            </div>
            );
    }
}

Suggestions.propTypes = {
    items: React.PropTypes.object,
    onSelected: React.PropTypes.func,
    onHovered: React.PropTypes.func,
    selected: React.PropTypes.number
};

export default Suggestions;