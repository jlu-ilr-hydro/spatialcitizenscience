import flask as flask
import markdown
from .configuration import get_config, to_yaml
from . import database as db

app = flask.Flask(__name__)


def render_markdown(filename, title=None):
    """
    Renders a markdown file to html
    :param filename: A markdown file to render
    :return: HTML version of the markdown file
    """
    with app.open_resource('markdown/' + filename) as f:
        text = f.read()
    text = markdown.markdown(text.decode())
    text = flask.Markup(text)
    return flask.render_template('markdown.html', markdown_content=text, title=title)


@app.route('/')
def mainpage():
    """
    Returns main.md
    :return:
    """
    return render_markdown("main.md")


@app.route('/blog')
def blog():
    return render_markdown('main.md')


@app.route('/map')
def map():
    return flask.render_template("map.html", title="map")


@app.route('/form')
def form():
    """
    Displays the data entry form. The data entry form uses the config.database.fields to show the entries
    """

    # Get values from a GET URL
    values = dict(
        lon=flask.request.args.get('longitude', ''),
        lat=flask.request.args.get('latitude', '')
    )

    config = get_config()

    # Helper dictionary to map the field.type value to a HTML input type
    input_types = dict(float='number', int='number', str='text', datetime='date', bytes='file')

    return flask.render_template("form.html", fields=config.database.fields,
                                 values=values, title="Eingabe", input_types=input_types)



@app.route('/about')
def about():
    return flask.render_template("about.html", title="About")


