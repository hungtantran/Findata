from flask import Flask, render_template, request
import json

app = Flask(__name__, static_url_path='', static_folder='static')
app.add_url_rule('/', 'index', lambda: render_template('index.html'))

@app.route('/search')
def doSearch():
    title = request.args.get('search', 'default title')
    return '{"graphModel": {"title": "%s"}, "tableModel": {"title": "%s"}}' % (title, title)

if __name__ == "__main__":
    app.run();