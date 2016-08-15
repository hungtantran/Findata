import init_app
from flask import Flask, render_template, request, redirect
import json
import copy
from constants_config import Config
from metrics_database import MetricsDatabase

def GetMetricsFromTicker(ticker):
    metrics_db = MetricsDatabase(
        'mysql',
         Config.mysql_username,
         Config.mysql_password,
         Config.mysql_server,
         Config.mysql_database,
         '%s_metrics'%ticker)
    try:
        data = {}
        data["adj_close"] = metrics_db.get_metrics("adj_close", reverse_order=True)
        data["vol"] = metrics_db.get_metrics("volume", reverse_order=True)
        return data
    except Exception as e:
        print e
        return []


app = Flask(__name__, static_url_path='', static_folder='static')
defaultTableModel = json.load(open('webserver/models/tablemodel.json', 'r'))
defaultGraphModel = json.load(open('webserver/models/graphmodel.json', 'r'))

app.add_url_rule('/', 'index', lambda: render_template('index.html'))
app.add_url_rule('/about', 'about', lambda: render_template('about.html'))
app.add_url_rule('/contact', 'contact', lambda: render_template('contact.html'))

@app.route('/search')
def doSearch():
    print "Running search..."
    graphModel = copy.deepcopy(defaultGraphModel)
    tableModel = copy.deepcopy(defaultTableModel)
    title = request.args.get('search', 'default title')
    graphModel["title"] = title
    metrics = GetMetricsFromTicker(title);
    graphModel["adj_close"] = [(x.start_date.isoformat(sep=' '), x.value) for x in metrics["adj_close"]]
    graphModel["vol"] = [(x.start_date.isoformat(sep=' '), x.value) for x in metrics["vol"]]
    tableModel["title"] = title
    for num, item in enumerate(title.split()):
        tableModel["data"].append(("Key%s" % num, item))

    print "Finishing search..."
    return '{"graphModel": %s, "tableModel": %s}' % (json.dumps(graphModel), json.dumps(tableModel))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True);