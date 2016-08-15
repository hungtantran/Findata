import React from 'react';

function getTranslation(left, top) {
    return `translate(${left}, ${top})`;
}

class Legend extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        var items = this.props.items.map((item, index)=> {
            var color = {fill: this.props.colorscale(index)};
            return <text x="2em" y={`${index}em`} style={color} key={`text${index}`}>{index}</text>;
        });

        var colors = this.props.items.map((item, index)=> {
            var cy = `${-.25 + 1*index}em`;
            var color = {fill: this.props.colorscale(index)};
            
            return <circle cx="1em" cy={cy} r="0.4em" style={color} key={`cirlce${index}`} />;
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