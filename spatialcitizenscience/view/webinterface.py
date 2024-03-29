import flask as flask
import flask_wtf
import wtforms

from ..configuration import Config
from .. import database as db
from .form import create_form_type
from .webtools import render_markdown

from pathlib import Path


ui = flask.Blueprint('ui', __name__, template_folder='../templates', static_folder='../static')
ui.app_template_filter('clean')

@ui.route('/', methods=['GET'])
def index():
    return content('')


@ui.route('/<path:page>', methods=['GET'])
def content(page):
    path = Path(flask.current_app.instance_path) / 'content' / page
    if path.is_dir():
        path /= 'index.md'
    else:
        path = path.with_suffix('.md')
    if path.exists():
        return render_markdown(path)

    flask.abort(404, f'{page} is not a configured content page')


@ui.route('/media/<path:filename>', methods=['GET'])
def media(filename):
    """
    Returns a file from the media directory
    :return:
    """
    media_path = flask.current_app.instance_path + '/media'
    return flask.send_from_directory(media_path, filename)


@ui.route('/form', methods=['GET', 'POST'])
def form():
    """
    Displays the data entry form. The data entry form uses the config.database.fields to show the entries
    """
    with Config() as config:
        F = create_form_type(config.database.fields)
        f: flask_wtf.FlaskForm = F()
        if f.validate_on_submit():
            with db.Connection(config) as con:
                con.write_entry(**f.data)
            return flask.redirect(flask.url_for('ui.map'))
        else:
            f.process(flask.request.args)
            return flask.render_template("form.html", form=f, title="Eingabe")


@ui.route('/edit', methods=['GET', 'POST'])
def edit():
    with Config() as config:
        F = create_form_type(config.database.fields, edit_id=True)
        f: flask_wtf.FlaskForm = F()
        if f.validate_on_submit():
            with db.Connection(config) as con:
                con.update_entry(**f.data)
            return flask.redirect(flask.url_for('ui.map'))
        else:
            with db.Connection(config) as con:
                entry: db.Entry = next(con.read_entries(**flask.request.args))
                f.process(entry)
            return flask.render_template("form.html", form=f, title="Eingabe")



@ui.route('/map', methods=['GET'])
def map():
    with Config() as config:
        return flask.render_template("map.html", title=config.map.title, map=config.map)


@ui.route('/sites.geojson', methods=['GET'])
def sites_geojson():
    """
    Returns all sites as geojson objects
    :return:
    """

    with Config() as config:
        with db.Connection(config) as con:
            features = con.features()
            features = list(features)
    return flask.jsonify(features)


@ui.route('/sites.csv', methods=['GET'])
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

    with Config() as config:
        with db.Connection(config) as con:
            writer.writerow(con.fieldnames)
            writer.writerows(con.read_entries())

    output = flask.make_response(dest.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=spatialcitizenscience.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@ui.route('/sites.map', methods=['GET'])
def sites_map():
    with Config() as config:
        return flask.render_template("map-sites.html", title=config.map.title, map=config.map)
