from collections import Counter, defaultdict
import datetime
import itertools
import json
import os
from typing import Any, Dict, List

from flask import Flask, render_template, session, redirect, url_for, jsonify, current_app
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import TimeField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError


from config import config
from nav import nav


def get_timestamp():
    today = datetime.datetime.now()
    return datetime.datetime(today.year, today.month, today.day, 19, 0, 0)


def number_to_word(n: Any):
        return {'1': "One", '2': "Two", '3': "Three", '4': "Four", '5': "Five", '6': "Six",
                '7': "Seven", '8': "Eight", '9': "Nine", '10': "Ten", '11': "Eleven", '12': "Twelve",
                '13': "Thirteen", '14': "Fourteen", '15': "Fifteen", '20': "Twenty", '25': "Twenty-Five", '30': 'Thirty'}.get(str(n))


class SettingsForm(FlaskForm):
    players = TextAreaField('Players', render_kw={"rows": 15, "cols": 1}, validators=[DataRequired()])
    courts = SelectField('Courts', choices=[(i, number_to_word(str(i))) for i in range(1, 13)], default=3)
    rounds = SelectField('Rounds', choices=[(i, number_to_word(str(i))) for i in range(1, 13)], default=8)
    start_time = TimeField('Start Time', format='%H:%M', default=get_timestamp())
    round_time = SelectField('Minutes Per Round', choices=[(str(i), number_to_word(str(i))) for i in range(5, 35, 5)], default=15)
    submit = SubmitField('Create Schedule')


def readable_schedule(players: list, sched: str, sep=' - '):
    """Creates readable schedule"""
    # data has players and schedule keys
    if not sched:
        return [1, 1, 'No available schedule', 'No available schedule']
    items = []
    if isinstance(sched, str):
        sched = json.loads(sched)
    for idx, rnd in enumerate(sched):
        court = 1
        for matchup in rnd:
            team1 = sep.join([players[int(i)].strip() for i in matchup[0:2]])
            team2 = sep.join([players[int(i)].strip() for i in matchup[2:]])            
            items.append([idx + 1, court, team1, team2])
            court += 1
    return items


def schedule_summary(players: List[str], sched: str) -> List[Dict[str, Any]]:
    """Summarizes schedule by player
    
    Keys:
        n_courts
        n_players
        opponent_dupcount
        partner_dupcount
        schedule - is a list of list of list of int
        each inner list is a pairing
        each outer list is a round
        the far outer list is the schedule

    """
    # build up lists of tuples
    # then can count at the end
    # ultimately want to implement this as part of schedule optimizer
    # this is a simple fix for the time being
    sched = json.loads(sched)

    partners = defaultdict(int)
    opponents = defaultdict(int)

    for rnd in sched:
        for matchup in rnd:
            team1 = tuple(sorted(matchup[0:2]))
            team2 = tuple(sorted(matchup[2:]))
            partners[team1] += 1
            partners[team2] += 1
            for opp in itertools.product(team1, team2):
                opponents[tuple(sorted(opp))] += 1

    dup_partners = {player: 0 for player in players}
    dup_opponents = {player: 0 for player in players}
    
    for pairing, cnt in partners.items():
        if cnt > 1:
            player1, player2 = pairing
            dup_partners[player1] += 1
            dup_partners[player2] += 1
            
    for pairing, cnt in opponents.items():
        if cnt > 1:
            player1, player2 = pairing
            dup_opponents[player1] += 1
            dup_opponents[player2] += 1
        
    return {'dup_partners': dup_partners, 'dup_opponents': dup_opponents}


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
        rs = readable_schedule(f['players'], sched)
        data = {**f, **{'schedule': rs}}
        return render_template('schedule.html', data=data)

    @app.route('/summary', methods=('GET',))
    def summary():
        return render_template('summary.html', data=session['form_data'])

    return app


def test_summ():
    """Tests the summary schedule"""
    sched = json.dumps([[[1, 2, 3, 4], [5, 6, 7, 8]], [[2, 1, 4, 3], [6, 7, 5, 8]]])
    r = schedule_summary(list(range(1, 9)), sched)
    assert r['dup_opponents'] == {1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 1, 7: 1, 8: 1}, r['dup_opponents']
    assert r['dup_partners'] == {1: 1, 2: 1, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0}, r['dup_partners']
    print('Tests passed!')


if __name__ == '__main__':
    create_app().run(debug=True)
    