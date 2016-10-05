import React from 'react';
import PlotDisplay from './plotDisplay';

class Plot extends React.Component {
    constructor(props) {
        super(props);
        this.getData = this.getData.bind(this);
        this.getPlotData = this.getPlotData.bind(this);

        this.plotDisplay = undefined;
        this.state = {
            data: {},
        };
    }

    getData(dataDesc) {
        var key = JSON.stringify(dataDesc);
        var data = this.state.data;
        if (!(key in data)) {
            data[key] = [];
            fetch($SCRIPT_ROOT + '/search', {
                mode: 'no-cors',
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action: "GetData",
                    metricName: dataDesc.metricName,
                    tableName: dataDesc.tableName,
                })
            }).then(function(response) {
                return response.json();
            }).catch(function(ex) {
                console.log('parsing failed', ex);
            }).then((json) => {
                console.log("New Data");
                data[key] = json;
                this.setState({
                    data: data
                });
            });
        }
        return data[key];
    }

    getPlotData() {
        // plotData is an array of map object that has 3 keys: title (string), type (string) and data (array) 
        var plotData = []
        for (var key in this.props.dataSets) {
            var dataSet = this.props.dataSets[key];
            var data = {};
            data["Title"] = dataSet.Title;
            data["Type"] = dataSet.Type;
            data["Data"] = this.getData(dataSet.DataDesc);
            plotData.push(data);
        }
        return plotData;
    }

    render() {
        var plotData = this.getPlotData();
        // Remove this hack to force child rerender
        var key = Math.random();
        return (
            <PlotDisplay
                key={key}
                width={this.props.width}
                height={this.props.height}
                xOffset={this.props.xOffset}
                yOffset={this.props.yOffset}
                title={this.props.title}
                plotData={plotData}
            />);
    }
}

Plot.propTypes = {
    width: React.PropTypes.number,
    height: React.PropTypes.number,
    xOffset: React.PropTypes.number,
    yOffset: React.PropTypes.number,
    title: React.PropTypes.object,
    dataSets: React.PropTypes.object
};

export default Plot;