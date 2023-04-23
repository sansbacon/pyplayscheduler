from collections import defaultdict
import json
import logging
import uuid

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session, url_for
from google.cloud import ndb

from main import client, mc
from forms import SettingsForm
from helper import create_optimal, create_schedule_key, parse_players, readable_schedule, schedule_summary
from model import CustomSchedule, OptimalSchedule


blueprint = Blueprint('blueprint', __name__, static_folder='static', template_folder='templates')


@blueprint.route('/', methods=('GET', 'POST'))
def index():
    form = SettingsForm(meta={'csrf': False})
    if all((request.method == 'GET', 'form_data' in session)):
        if players := session['form_data'].get('players'):
            form.players.data = '\n'.join(players)
        if n_courts := session['form_data'].get('n_courts'):
            form.courts.data = int(n_courts)
        if n_rounds := session['form_data'].get('n_rounds'):
            form.rounds.data = int(n_rounds)

    if form.validate_on_submit():
        # the schedule generation logic needs to be here
        # the schedule page can then be a lookup and display
        data = session.get('form_data')
        skey = create_schedule_key(data.get('n_courts'), data.get('n_rounds'), data.get('n_players'))

        # look up the optimal schedule in the app
        optimal = current_app.schedule.get(skey)

        # if not in the app, see if it is in the cache
        if not optimal:
            optimal = mc.get(skey)

        # if not in the cache, check the datastore
        if not optimal:
            optimal = OptimalSchedule.find_by_id(skey)
            mc.put(skey, optimal)
        
        # if not in the datastore, generate new optimal
        if not optimal:
            optimal = create_optimal(data.get('n_courts'), data.get('n_rounds'), data.get('n_players'))
            mc.put(skey, optimal)
            
            with client.context():
                optimal.put()

        custom_sched = CustomSchedule(
            n_courts=form.courts.data,
            n_rounds=form.rounds.data,
            players=parse_players(form.players.data),
            optimal_schedule=optimal
        )

        # put schedule in session, cache, and datastore
        session[custom_sched.custom_schedule_id] = custom_sched.to_json()
        mc.put(custom_sched.custom_schedule_id, custom_sched)
        with client.context():
            custom_sched.put()

        return redirect(url_for('blueprint.schedule', id=custom_sched.custom_schedule_id))
    return render_template('index.html', form=form)


    @blueprint.route('/schedule', methods=('GET', 'POST'))
    def schedule():
        # if no schedule id, then redirect to schedule form
        schedule_id = request.args.get('id')
        if not schedule_id:
            redirect(url_for('blueprint.index'))

        # find the schedule
        # try the session first
        try:
            schedule = CustomSchedule.from_json(session.get(schedule_id))
        except:
            schedule = None
            
        # try the cache
        if not schedule:
            schedule = mc.get(schedule_id)

        # try the datastore
        if not schedule:
            with client.context():
                schedule = CustomSchedule.find_by_id(schedule_id)
                mc.put(schedule_id, schedule)

        # create the readable schedule        
        _ = schedule.readable_schedule()
        return render_template('schedule.html', data=schedule.to_dict())


@blueprint.route('/summary', methods=('GET',))
def summary():
    """Summarizes schedule by player, partner_dupcounts, opp_dupcounts"""
    data = defaultdict(list)
    f = session['form_data']
    skey = create_schedule_key(f['courts'], f['rounds'], len(f['players']))
    logging.info(f"Schedule key is {skey}")

    if schedule := mc.get(skey):
        logging.info("Found schedule in memcache")
        schedule = json.loads(schedule)
    else:
        logging.info('Got schedule from app')
        schedule = f.get('schedule', current_app.schedule.get((int(f['courts']), int(f['rounds']), len(f['players']))))
    if not schedule:
        raise ValueError(f'Cannot find schedule for {skey}')
    logging.info(f'Schedule type is {str(type(schedule))}')
    partners, opponents = schedule_summary(f['players'], schedule)
    logging.info(json.dumps(partners))
    logging.info(json.dumps(opponents))
    for (k, v), (k2, v2) in zip(partners.items(), opponents.items()):
        data['summary'].append([k, v, v2])       
    return render_template('summary.html', data=data)