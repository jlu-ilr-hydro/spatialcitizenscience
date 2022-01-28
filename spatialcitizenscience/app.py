
import flask
from pathlib import Path

from .configuration import Config
from . import database as db


def create_app():

    app = flask.Flask(__name__, instance_path=str(Path('.').absolute()))
    with Config() as config:
        app.config.from_mapping(config)
        app.add_template_global(config, 'config')
    db.debug = app.config['DEBUG']
    return app


app = create_app()
