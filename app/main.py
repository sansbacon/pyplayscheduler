import json
import logging
import os
import sys

from flask import Flask
from flask_bootstrap import Bootstrap
from google.appengine.api import wrap_wsgi_app
from google.appengine.api.memcache import Client
import google.cloud.logging as gcl

from blueprints import blueprint
from config import config
from nav import nav

# logging
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

# memcache
mc = Client()

# app
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'dev')])
app.secret_key = 'xyzabc'
app.wsgi_app = wrap_wsgi_app(app.wsgi_app)
filename = os.path.join(app.static_folder, 'schedule.json')
with open(filename) as fh:
    app.optimal_schedules = {f"schedule_{item['n_courts']}_{item['n_rounds']}_{item['n_players']}": item['schedule'] 
                             for item in json.load(fh)}
app.register_blueprint(blueprint)
Bootstrap(app)
nav.init_app(app)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    