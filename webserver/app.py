import init_app
from flask import Flask, render_template, request, redirect
import json
import copy
from constants_config import Config
from metrics_database import MetricsDatabase

class VizType():
    Line = "line"
    Bar = "bar"

class DataPair():
    def __init__(self, date, value):
        self.t = date
        self.v = value

class Model():
    def __init__(self):
        self.graphs = {}

    def addGraph(self, key, graph):
        self.graphs[key] = graph

class Graph():
    def __init__(self, title):
        self.plots = {}

    def addPlot(self, key, plot):
        self.plots[key] = plot

class Plot():
    def __init__(self, title):
        self.title = title
        self.dataSets = {}

    def addDataSet(self, key, dataSet):
        self.dataSets[key] = dataSet

class DataSet():
    def __init__(self, title, type, data):
        self.title = title
        self.type = type
        self.data = DataSet.RawToTimeSeries(data)

    @staticmethod
    def RawToTimeSeries(rawData):
        rawData = [(x.start_date.isoformat(sep=' '), x.value) for x in rawData]
        data = []
        for datum in rawData:
            data.append(DataPair(datum[0], datum[1]))
        return data

global_model = Model()

def GetMetricsFromTicker(ticker):
    metrics_db = MetricsDatabase(
        'mysql',
         Config.mysql_username,
         Config.mysql_password,
         Config.mysql_server,
         Config.mysql_database,
         '%s_metrics'%ticker)
    try:
        graph = Graph(ticker)
        volume_plot = Plot(ticker)
        adj_close_plot = Plot(ticker)

        adj_close_plot.addDataSet(ticker, DataSet( "%s Adjusted Close" % ticker, VizType.Line, metrics_db.get_metrics("adj_close", reverse_order=True)))
        volume_plot.addDataSet(ticker, DataSet( "%s Volume" % ticker, VizType.Bar, metrics_db.get_metrics("volume", reverse_order=True)))
        graph.addPlot("adj_close_%s" % ticker, adj_close_plot)
        graph.addPlot("volume_%s" % ticker, volume_plot)
        global_model.addGraph(ticker, graph)
        return global_model
    except Exception as e:
        print e
        return Model()


app = Flask(__name__, static_url_path='', static_folder='static')
defaultTableModel = json.load(open('webserver/models/tablemodel.json', 'r'))
defaultGraphModel = json.load(open('webserver/models/graphmodel.json', 'r'))

app.add_url_rule('/', 'index', lambda: render_template('index.html'))
app.add_url_rule('/about', 'about', lambda: render_template('about.html'))
app.add_url_rule('/contact', 'contact', lambda: render_template('contact.html'))

@app.route('/search')
def doSearch():
    print "Running search..."
    title = request.args.get('search', 'default title')
    graphModel = Model()
    if title == "clear":
        global_model = Model()
    else:
        graphModel = GetMetricsFromTicker(title);

    print "Finishing search..."
    return '{"graphModel": %s}' % (json.dumps(graphModel, default=lambda o: o.__dict__))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True);