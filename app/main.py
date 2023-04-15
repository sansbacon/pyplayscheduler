import json
import os

from flask import Flask
from flask_bootstrap import Bootstrap

from blueprints import blueprint
from config import config
from nav import nav


app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'dev')])
app.secret_key = 'xyzabc'
filename = os.path.join(app.static_folder, 'schedule.json')
with open(filename) as test_file:
    app.schedule = {(item['n_courts'], item['n_rounds'], item['n_players']): item['schedule'] for item in json.load(test_file)}
app.register_blueprint(blueprint)
Bootstrap(app)
nav.init_app(app)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    