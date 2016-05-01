from flask import Flask, render_template, request
import json

app = Flask(__name__, static_url_path='', static_folder='static')
app.add_url_rule('/', 'index', lambda: render_template('index.html'))

tableModel = {
    "title": "",
    "data": []
}

graphModel = {
    "title": ""
}

@app.route('/search')
def doSearch():
    title = request.args.get('search', 'default title')
    graphModel["title"] = title
    tableModel["title"] = title
    tableModel["data"] = [("Key1", "Val1"), ("Key2", "Val2"), ("Key3", "Val3"), ("Key4", "Val4"), ("Key5", "Val5")]
    return '{"graphModel": %s, "tableModel": %s}' % (json.dumps(graphModel), json.dumps(tableModel))

if __name__ == "__main__":
    app.run();