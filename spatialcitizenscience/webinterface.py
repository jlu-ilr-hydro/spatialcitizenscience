import flask as flask
import markdown
import geojson

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


@app.route('/', methods=['GET'])
def mainpage():
    """
    Returns main.md
    :return:
    """
    config = get_config()
    return render_markdown(config.content.main)


@app.route('/blog', methods=['GET'])
def blog():
    return render_markdown('main.md')


@app.route('/map', methods=['GET'])
def map():
    return flask.render_template("map.html", title="map")


@app.route('/form', methods=['GET'])
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


@app.route('/save', methods=['POST'])
def save():
    """
    Saves the data from form to the database, accepts only POST data
    """
    db.debug = True
    with db.Connection(app.root_path) as con:

        # Translate the request.form dictionary (with strings)
        # to a dictionary that maps from field name to the value of the correct type
        # Uses db.str_to_python_type dictionary to create the right type
        result = {}
        for f in con.fields:
            if f.name in flask.request.form:
                result[f.name] = db.str_to_python_type[f.type](flask.request.form.get(f.name))

        # Write the result into the database
        con.write_entry(**result)
        con.commit()

    db.debug = False
    # Return to map
    return flask.redirect(flask.url_for('map'))


@app.route('/about', methods=['GET'])
def about():
    return flask.render_template("about.html", title="About")


@app.route('/sites.geojson', methods=['GET'])
def sites_geojson():
    """
    Returns all sites as geojson objects
    :return:
    """

    with db.Connection(app.root_path) as con:
        return flask.jsonify(list(con.features()))

