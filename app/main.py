import datetime
import json
import os
import re

from flask import Flask, render_template, session, redirect, url_for, request, current_app
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import TimeField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError


from config import config
from nav import nav



def get_timestamp():
    today = datetime.datetime.now()
    return datetime.datetime(today.year, today.month, today.day, 19, 0, 0)


def number_to_word(n):
        return {'1': "One", '2': "Two", '3': "Three", '4': "Four", '5': "Five", '6': "Six",
                '7': "Seven", '8': "Eight", '9': "Nine", '10': "Ten", '11': "Eleven", '12': "Twelve",
                '13': "Thirteen", '14': "Fourteen", '15': "Fifteen", '20': "Twenty", '25': "Twenty-Five", '30': 'Thirty'}.get(n)


class SettingsForm(FlaskForm):
    courts = SelectField('Courts', choices=[(i, number_to_word(str(i))) for i in range(1, 13)], default=3)
    rounds = SelectField('Rounds', choices=[(i, number_to_word(str(i))) for i in range(1, 13)], default=8)
    players = TextAreaField('Players', render_kw={"rows": 15, "cols": 1}, validators=[DataRequired()])
    #start_time = TimeField('Start Time', format='%H:%M', default=get_timestamp())
    #round_time = SelectField('Minutes Per Round', choices=[(str(i), number_to_word(str(i))) for i in range(5, 35, 5)], default=15)
    submit = SubmitField('Create Schedule')

    def validate_players(form, field):
        names = [s for s in re.split('\s+', field.data) if s]
        courts = int(form.courts.data)
        min_players = courts * 4
        if len(names) < min_players:
            msg = f'ERROR: You only have {len(names)} players and need a minimum of {min_players} to fill {courts} courts. Increase the number of players or reduce the number of courts.'
            raise ValidationError(msg)

def readable_schedule(players: list, sched: str, sep=' - '):
    """Creates readable schedule"""
    # data has players and schedule keys
    if not sched:
        return [[1, 1, 'No available schedule', 'Please try again']]
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


app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'dev')])
app.secret_key = 'xyzabc'
filename = os.path.join(app.static_folder, 'schedule.json')
with open(filename) as test_file:
    app.schedule = {(item['n_courts'], item['n_rounds'], item['n_players']): item['schedule'] for item in json.load(test_file)}
Bootstrap(app)
nav.init_app(app)

@app.route('/', methods=('GET', 'POST'))
def setup():
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
            'players': [str(i) for i in form.players.data.split('\n')], 
            'rounds': form.rounds.data, 
            'courts': form.courts.data
        }
        return redirect(url_for('schedule'))
    return render_template('index.html', form=form)

@app.route('/schedule', methods=('GET',))
def schedule():
    try:
        f = session['form_data']
        sched = current_app.schedule.get((int(f['courts']), int(f['rounds']), len(f['players'])))
        rs = readable_schedule(f['players'], sched)
    except:
        rs = [[1, 1, 'No available schedule', 'Please try again']]
    data = {**f, **{'schedule': rs}}
    return render_template('schedule.html', data=data)

@app.route('/summary', methods=('GET',))
def summary():
    return render_template('summary.html', data=session['form_data'])



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)