import flask as flask
import markdown
import bleach
from pathlib import Path

from .configuration import Config
from . import database as db
from .form import create_form_type


def create_app():
    app = flask.Flask(__name__, instance_path=str(Path('.').absolute()))
    print('Using configuration from: ', app.instance_path)
    with Config() as config:
        app.config.from_mapping(config)
        print(config)
    db.debug = app.config['DEBUG']
    return app


app = create_app()


def clean(text: str):

    return flask.Markup(
        bleach.clean(
            text,
            bleach.ALLOWED_TAGS + ['sub', 'sup'],
            ['class']
        )
    )


def render(template, title=None, **kwargs):
    with Config() as config:
        return flask.render_template(
            template, title=clean(title or config['title']),
            **kwargs,
            config=config, clean=clean
        )


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
    return render('markdown.html', markdown_content=text, title=title)


@app.route('/', methods=['GET'])
def index():
    """
    Returns main.md
    :return:
    """
    with Config() as config:
        return render_markdown(config.content.index.text)


@app.route('/map', methods=['GET'])
def map():
    with Config() as config:
        return render("map.html", title="map", map=config.map, showsites=False)


@app.route('/form', methods=['GET', 'POST'])
def form():
    """
    Displays the data entry form. The data entry form uses the config.database.fields to show the entries
    """
    req = flask.request
    with Config() as config:
        F = create_form_type(config.database.fields, use_flask_wtf=True)
        f = F()

        if f.validate_on_submit():
            with db.Connection(app.instance_path, config.database) as con:
                con.write_entry(**f.data)
            return flask.redirect(flask.url_for('map'))
        else:
            for k, v in flask.request.args.items():
                f[k].data = v
            return render("form.html", form=f, title="Eingabe")



@app.route('/about', methods=['GET'])
def about():
    return render_markdown('about.md', 'Über')


@app.route('/sites.geojson', methods=['GET'])
def sites_geojson():
    """
    Returns all sites as geojson objects
    :return:
    """

    with db.Connection(app.root_path) as con:
        features = con.features()
        features = list(features)
        return flask.jsonify(features)


@app.route('/sites.csv', methods=['GET'])
def sites_csv():
    """
    Returns all sites as geojson objects
    :return:
    """
    import io
    import csv

    dest = io.StringIO()
    dest.write('\ufeff')
    writer = csv.writer(dest, quoting=csv.QUOTE_MINIMAL)

    with db.Connection(app.root_path) as con:
        writer.writerow(con.fieldnames)
        writer.writerows(con.read_entries())
    output = flask.make_response(dest.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=spatialcitizenscience.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/sites.map', methods=['GET'])
def sites_map():
    with Config() as config:
        return flask.render_template("map.html", title=config.map.title, map=config.map, showsites=True)
