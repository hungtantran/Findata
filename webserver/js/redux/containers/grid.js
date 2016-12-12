import {connect} from 'react-redux';
import React from 'react';
import { updateGridLayout } from '../actions/gridActions';
import { removeElement } from '../actions/elementActions';
import Graph from './graph';

class Grid extends React.Component {

    constructor(props) {
        super(props);

        this.removeItem = this.removeItem.bind(this)
        this.addGraphs = this.addGraphs.bind(this);
        this.exportGraphState = this.exportGraphState.bind(this);

        this.numColumns = 48;
        this.width = screen.width * 0.90;
        this.cellSize = this.width / this.numColumns;

        this.defaultGraphWidthInCell = 15;
        this.defaultGraphHeightInCell = 10;
        this.defaultGraphContainerWidthInCell = 16;
        this.defaultGraphContainerHeightInCell = 11;
    }

    // Function call to serialize the current gridstack information and send to workspace
    exportGraphState() {
        var res = {};
        _.map($('.grid-stack .grid-stack-item:visible'), function (el) {
            el = $(el);
            var node = el.data('_gridstack_node');
            if (node === undefined)
                return;
            
            var id = el.attr('id');
            res[id] = {
                x: node.x,
                y: node.y,
                width: node.width,
                height: node.height,
            };
        }.bind(this));
        if(Object.keys(res).length == Object.keys(this.props.elements).length)
            this.props.onLayoutChange(res);
    }

    // Function call when there is new update to the dom to add new graph to the gridstacl
    // TODO: in the future, thing change doesn't mean new graph
    addGraphs() {
        var grid = $('.grid-stack').data('gridstack');

        grid.batchUpdate();
        grid.removeAll(false);

        Object.keys(this.props.elements).forEach((key) => {
            let element = this.props.elements[key];
            var x = element.x <= 0 ? 0 : element.x;
            var y = element.y <= 0 ? 0 : element.y;
            var width = element.width <= 0 ? 6 : element.width;
            var height = element.height <= 0 ? 8 : element.height;
            var node = {
                x: x,
                y: y,
                width: width,
                height: height,
            };

            grid.addWidget(
                $('#' + key),
                node.x,
                node.y,
                node.width,
                node.height);
        });
        grid.commit();
    }

    componentDidMount() {
        $(function () {
            var options = {
                verticalMargin: 0,
                //float: true
                draggable: {handle: '.grid-stack-item-content', scroll: false, appendTo: 'body', cancel: '.legendItem'},
                resizable: {
                    handles: 'se, sw'
                }            
            };
            $('.grid-stack').gridstack(options);
        });

        $('.grid-stack').on('change', this.exportGraphState);
    }

    componentDidUpdate(prevProps) {
        this.addGraphs(prevProps.elements);
    }

    shouldComponentUpdate(nextProps) {
        if (Object.keys(this.props.elements).length != Object.keys(nextProps.elements).length) {
            return true;
        }
        for(var id in this.props.elements) {
            if(!nextProps.elements[id])
                return true;
        }
        return false;
    }

    removeItem(clickEvent) {
        this.props.removeElement(clickEvent.target.id);
    }

    render() {
        let elements = Object.keys(this.props.elements).map((id) => {
            return (
            <div className="grid-stack-item" id={id} key={id}>
                <span style={{float:'left', display:'inline-block', position:'absolute', zIndex: '9999'}} onClick={this.removeItem}>
                    <img
                        id={id}
                        src='https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcRzUypyvRutgLIArGpLOSEyT6noe39ZYiJKbzbvPVaE1ZTXEure'
                        style={{width: '10px', height: '10px'}}/>
                </span>
                <div className="grid-stack-item-content" style={{left: 0, right: 0}}>
                    <Graph id={id} key={id} />
                </div>
            </div>
            );
        });

        return (
            <div>
                <div className="grid-stack" data-gs-width="12" data-gs-animate="yes">
                {elements}
                </div>
            </div>
        );
    }
}

Grid.propTypes = {
    elements: React.PropTypes.object, 
    onLayoutChange: React.PropTypes.func,
    removeElement: React.PropTypes.func
};

const mapStateToProps = (state) => {

    let applicableIDs = state.dashboardTabs.tabs[state.dashboardTabs.activeTab];

    let elements = {};
    applicableIDs.forEach((id) => {
        elements[id] = state.elements[id];
    });

    return {
        elements: elements
    };
};

const mapDispatchToProps = (dispatch) => {
    return {
        onLayoutChange: (gridLayoutUpdate) => dispatch(updateGridLayout(gridLayoutUpdate)),
        removeElement: (elementId) => dispatch(removeElement(elementId))
    };
};

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Grid);