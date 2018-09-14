import flask as flask
import markdown
from .configuration import get_config, to_yaml
from . import database as db

app = flask.Flask(__name__)


def render_markdown(filename):
    with app.open_resource('markdown/' + filename) as f:
        text = f.read()
    text = markdown.markdown(text.decode())
    text = flask.Markup(text)
    return flask.render_template('markdown.html', markdown_content=text)

@app.route('/')  # mehere Namen sind gleichzietig moeglich
def mainpage():
    return render_markdown("main.md")


@app.route('/blog')
def blog():
    return render_markdown('main.md')


@app.route('/map')
def map():
    return flask.render_template("map.html", title="map")


@app.route('/form')
def form():
    values = dict(
        lon=flask.request.args.get('longitude', ''),
        lat=flask.request.args.get('latitude', '')
    )
    config = get_config()
    input_types = dict(float='number', int='number', str='text', datetime='date', bytes='file')
    return flask.render_template("form.html", fields=config.database.fields,
                                 values=values, title="Eingabe", input_types=input_types)



@app.route('/about')
def about():
    return flask.render_template("about.html", title="About")


