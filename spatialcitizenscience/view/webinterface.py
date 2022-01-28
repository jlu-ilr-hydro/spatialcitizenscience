import flask as flask

from ..configuration import Config
from .. import database as db
from .form import create_form_type
from .. import app
from .webtools import render_markdown


@app.route('/', methods=['GET'])
def index():
    """
    Returns main.md
    :return:
    """
    with Config() as config:
        return render_markdown(config.content.index.text)


@app.route('/media/<path:filename>', methods=['GET'])
def media(filename):
    """
    Returns a file from the media directory
    :return:
    """
    media_path = app.instance_path + '/media'
    return flask.send_from_directory(media_path, filename)


@app.route('/map', methods=['GET'])
def map():
    with Config() as config:
        return flask.render_template("map.html", title="map", map=config.map, showsites=False)


@app.route('/form', methods=['GET', 'POST'])
def form():
    """
    Displays the data entry form. The data entry form uses the config.database.fields to show the entries
    """
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
            return flask.render_template("form.html", form=f, title="Eingabe")


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
