__version__ = '2022.01.31a0'

import os

import os
import flask
from pathlib import Path

from .configuration import Config
from . import database as db
from . import view


def create_app(test_config=None):
    home = Config.find_home()
    app = flask.Flask(__name__, instance_path=str(home.absolute()))
    with Config() as config:
        app.config.from_mapping(config)
        app.add_template_global(config, 'config')
        app.register_blueprint(view.ui, url_prefix=config.base_url)
    if test_config:
        app.config.from_mapping(test_config)
    app.add_template_filter(view.clean)
    db.debug = app.config['DEBUG']
    return app


if __name__ == "__main__":
    app = create_app()
    os.environ['FLASK_DEBUG'] = 1
    app.run(debug=True)  # server neustart bei Veraenderungen wird vermieden

