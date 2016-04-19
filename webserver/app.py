from flask import Flask, render_template
from flask.ext.bower import Bower

app = Flask(__name__, static_url_path='', static_folder='static')
app.add_url_rule('/', 'root', lambda: render_template('index.html'))
Bower(app)

if __name__ == "__main__":
    app.run();