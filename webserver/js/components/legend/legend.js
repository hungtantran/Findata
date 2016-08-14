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
            return <text x="1em" y={`${index}em`} key={`text${index}`}>{index}</text>;
        });

        var colors = this.props.items.map((item, index)=> {
            var cy = `${-.25 + 1*index}em`;
            var color = {fill: this.props.colorscale(index)};
            
            return <circle cx="0" cy={cy} r="0.4em" style={color} key={`cirlce${index}`} />;
        });

        return (
            <svg className="legend" transform={getTranslation(this.props.xpos, this.props.ypos)} >
                {items}
                {colors}
            </svg>
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