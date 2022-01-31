
import flask
from pathlib import Path

from .configuration import Config
from . import database as db
from . import view

def create_app():

    app = flask.Flask(__name__, instance_path=str(Path('.').absolute()))
    Config.set_home(app.instance_path)
    with Config() as config:
        app.config.from_mapping(config)
        app.add_template_global(config, 'config')
    app.register_blueprint(view.ui)
    app.add_template_filter(view.clean)
    db.debug = app.config['DEBUG']
    return app


app = create_app()
