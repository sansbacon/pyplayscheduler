
import re

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
from google.appengine.api.memcache import Client

from forms import SettingsForm
from helper import create_optimal, readable_schedule, schedule_summary, ts


blueprint = Blueprint('blueprint', __name__, static_folder='static', template_folder='templates')
mc = Client()


@blueprint.route('/', methods=('GET', 'POST'))
def index():
    form = SettingsForm(meta={'csrf': False})
    if all((request.method == 'GET', 'form_data' in session)):
        if players := session['form_data'].get('players'):
            form.players.data = '\n'.join(players)
        if n_courts := session['form_data'].get('n_courts'):
            form.courts.data = n_courts
        if n_rounds := session['form_data'].get('n_rounds'):
            form.rounds.data = n_rounds
    if form.validate_on_submit():
        mc.add('ts', ts())
        session['form_data'] = {
            'players': [str(i).strip() for i in re.split(r'[\n\r]+', form.players.data) if re.search(r'\w+', i)], 
            'rounds': form.rounds.data, 
            'courts': form.courts.data
        }
        return redirect(url_for('blueprint.schedule'))
    return render_template('index.html', form=form)


@blueprint.route('/schedule', methods=('GET',))
def schedule():
    if f := session['form_data']:
        sched = current_app.schedule.get((int(f['courts']), int(f['rounds']), len(f['players'])))
        if sched:
            rs = readable_schedule(f['players'], sched)
        else:
            params = {
              'n_rounds': int(f['rounds']),
              'n_courts': int(f['courts']), 
              'n_players': len(f['players']),
              'iterations': 25000
            }
            rs = readable_schedule(f['players'], create_optimal(**params))
    else:
        rs = [[1, 1, 'No available schedule', 'Please try again']]
    data = {**f, **{'schedule': rs}}
    return render_template('schedule.html', data=data)


@blueprint.route('/summary', methods=('GET',))
def summary():
    try:
        f = session['form_data']
        players = f['players']
        schedule = f.get('schedule', current_app.schedule.get((int(f['courts']), int(f['rounds']), len(players))))
        partners, opponents = schedule_summary(players, schedule)
        data = {'summary': []}

        for (k, v), (k2, v2) in zip(partners.items(), opponents.items()):
            data['summary'].append([k, v, v2])       
    except:
        data = {'summary': [[1, 'No available schedule', 'Please try again']]}
    return render_template('summary.html', data=data)


@blueprint.route('/newschedule', methods=('POST',))
def newschedule():
    """Generates new schedule if optimal not already found"""
    content = request.json
    params = {
        'n_rounds': content['n_rounds'],
        'n_courts': content['n_courts'],
        'player_names': content['players'],
        'n_players': content.get('n_players', len(content['players'])),
        'iterations': 25000
    }
    return jsonify(create_optimal(**params))