import json
import os

from flask import Flask, render_template, session, redirect, url_for, current_app
from flask_bootstrap import Bootstrap

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
    Bootstrap(app)
    nav.init_app(app)

    @app.route('/', methods=('GET', 'POST'))
    def setup():
        form = SettingsForm(meta={'csrf': False})
        if form.validate_on_submit():
            session['form_data'] = {
                'players': [str(i) for i in form.players.data.split('\n')], 
                'rounds': form.rounds.data, 
                'courts': form.courts.data
            }
            return redirect(url_for('schedule'))
        return render_template('index.html', form=form)

    @app.route('/schedule', methods=('GET',))
    def schedule():
        f = session['form_data']
        sched = current_app.schedule.get((int(f['courts']), int(f['rounds']), len(f['players'])))
        session['form_data']['schedule'] = sched
        rs = readable_schedule(f['players'], sched)
        data = {**f, **{'schedule': rs}}
        return render_template('schedule.html', data=data)

    @app.route('/summary', methods=('GET',))
    def summary():
        f = session['form_data']
        players = f['players']
        schedule = f.get('schedule', current_app.schedule.get((int(f['courts']), int(f['rounds']), len(players))))
        partners, opponents = schedule_summary(players, schedule)
        data = {'summary': []}

        for (k, v), (k2, v2) in zip(partners.items(), opponents.items()):
            data['summary'].append([k, v, v2])       

        return render_template('summary.html', data=data)

    return app


if __name__ == '__main__':
    create_app().run(debug=True)
    