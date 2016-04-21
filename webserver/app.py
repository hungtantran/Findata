from flask import Flask, render_template

app = Flask(__name__, static_url_path='', static_folder='static')
app.add_url_rule('/', 'index', lambda: render_template('index.html'))

if __name__ == "__main__":
    app.run();