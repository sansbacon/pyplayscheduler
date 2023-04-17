from collections import defaultdict
import json
import logging
import re
import sys

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
from google.appengine.api.memcache import Client
import google.cloud.logging as gcl

from forms import SettingsForm
from helper import create_optimal, readable_schedule, schedule_key, schedule_summary


blueprint = Blueprint('blueprint', __name__, static_folder='static', template_folder='templates')
mc = Client()

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


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
        session['form_data'] = {
            'players': [str(i).strip() for i in re.split(r'[\n\r]+', form.players.data) if re.search(r'\w+', i)], 
            'rounds': form.rounds.data, 
            'courts': form.courts.data
        }
        return redirect(url_for('blueprint.schedule'))
    return render_template('index.html', form=form)


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
    schedule = create_optimal(**params)
    key = schedule_key(params['n_courts'], params['n_rounds'], params['n_players'])
    logging.info(f"Schedule key is {key}")
    logging.info(f"Schedule is {json.dumps(schedule['schedule'].tolist())}")
    mc.add(key, schedule['schedule'])
    return jsonify(schedule)


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
            sched = create_optimal(**params)
            rs = readable_schedule(f['players'], sched)
    else:
        rs = [[1, 1, 'No available schedule', 'Please try again']]
    key = schedule_key(f['courts'], f['rounds'], len(f['players']))
    logging.info(f"Schedule key is {key}")
    logging.info(f"Readable schedule is {json.dumps(rs)}")
    mc.add(key, json.dumps(sched))
    mc.add('rs', json.dumps(rs))
    data = {**f, **{'schedule': rs}}
    return render_template('schedule.html', data=data)


@blueprint.route('/summary', methods=('GET',))
def summary():
    """Summarizes schedule by player, partner_dupcounts, opp_dupcounts"""
    data = defaultdict(list)
    f = session['form_data']
    key = schedule_key(f['courts'], f['rounds'], len(f['players']))
    logging.info(f"Schedule key is {key}")

    if schedule := mc.get(key):
        logging.info("Found schedule in memcache")
        schedule = json.loads(schedule)
    else:
        logging.info('Got schedule from app')
        schedule = f.get('schedule', current_app.schedule.get((int(f['courts']), int(f['rounds']), len(f['players']))))
    if not schedule:
        raise ValueError(f'Cannot find schedule for {schedule_key}')
    logging.info(f'Schedule type is {str(type(schedule))}')
    partners, opponents = schedule_summary(f['players'], schedule)
    logging.info(json.dumps(partners))
    logging.info(json.dumps(opponents))
    for (k, v), (k2, v2) in zip(partners.items(), opponents.items()):
        data['summary'].append([k, v, v2])       
    return render_template('summary.html', data=data)