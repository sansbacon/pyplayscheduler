import json
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from blueprints import blueprint
from config import config
from forms import SettingsForm
from nav import nav
from helper import readable_schedule, schedule_summary


def create_app(app_environment=None):
    if app_environment is None:
        app = Flask(__name__)
        app.config.from_object(config[os.getenv('FLASK_ENV', 'dev')])
    else:
        app = Flask(__name__)
        app.config.from_object(config[app_environment])
    app.secret_key = 'xyzabc'
    filename = os.path.join(app.static_folder, 'schedule.json')
    with open(filename) as test_file:
        app.schedule = {(item['n_courts'], item['n_rounds'], item['n_players']): item['schedule'] for item in json.load(test_file)}
    app.register_blueprint(blueprint)
    Bootstrap(app)
    nav.init_app(app)
    return app


if __name__ == '__main__':
    create_app().run(debug=True)
    