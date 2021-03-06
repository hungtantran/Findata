import React from 'react';

function getTranslation(left, top) {
    return `translate(${left}, ${top})`;
}

class Legend extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        var items = Array.from(this.props.items, (val, index) => {
            var key = val.Title;
            var color = { fill: this.props.colorscale(key) };
            return (
                <text x="2em" y={`${index}em`} style={color} key={`text${key}`}>
                    {key}
                </text>
            );
        });

        var colors = Array.from(this.props.items, (val, index) => {
            var key = val.Title;
            var cy = `${-.25 + 1*index}em`;
            var color = { fill: this.props.colorscale(key) };
            return <circle cx="1em" cy={cy} r="0.4em" style={color} key={`cirlce${key}`} />;
        });

        return (
            <g className="legend" transform={getTranslation(this.props.xpos, this.props.ypos)} >
                {items}
                {colors}
            </g>
        );
    }
}

Legend.propTypes = {
    xpos: React.PropTypes.number,
    ypos: React.PropTypes.number,
    items: React.PropTypes.array,
    colorscale: React.PropTypes.func
};

export default Legend;