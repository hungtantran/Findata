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
        self.title = title
        self.dataSets = {}

    def addDataSet(self, key, dataSet):
        self.dataSets[key] = dataSet
        pass

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

def GetMetricsFromTicker(ticker):
    metrics_db = MetricsDatabase(
        'mysql',
         Config.mysql_username,
         Config.mysql_password,
         Config.mysql_server,
         Config.mysql_database,
         '%s_metrics'%ticker)
    try:
        model = Model()
        adj_close_graph = Graph(ticker)
        volume_graph = Graph(ticker)
        print "Getting adj close"
        adj_close_graph.addDataSet(ticker, DataSet( "%s Adjusted Close" % ticker, VizType.Line, metrics_db.get_metrics("adj_close", reverse_order=True)))
        print "Getting volume"
        volume_graph.addDataSet(ticker, DataSet( "%s Volume" % ticker, VizType.Bar, metrics_db.get_metrics("volume", reverse_order=True)))
        print "Adding graphs to model"
        model.addGraph("adj_close_%s" % ticker, adj_close_graph)
        model.addGraph("volume_%s" % ticker, volume_graph)
        return model
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
    graphModel = GetMetricsFromTicker(title);

    print "Finishing search..."
    return '{"graphModel": %s}' % (json.dumps(graphModel, default=lambda o: o.__dict__))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True);