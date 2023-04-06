import datetime
import os

from flask import Flask, render_template, redirect, url_for, session, jsonify, request
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
    players = TextAreaField('Players', render_kw={"rows": 15, "cols": 1}, validators=[DataRequired()])
    courts = SelectField('Courts', choices=[(i, number_to_word(str(i))) for i in range(1, 13)], default=3)
    rounds = SelectField('Rounds', choices=[(i, number_to_word(str(i))) for i in range(1, 13)], default=8)
    start_time = TimeField('Start Time', format='%H:%M', default=get_timestamp())
    round_time = SelectField('Minutes Per Round', choices=[(str(i), number_to_word(str(i))) for i in range(5, 35, 5)], default=15)
    submit = SubmitField('Create Schedule')


def create_app(app_environment=None):
    if app_environment is None:
        app = Flask(__name__)
        app.config.from_object(config[os.getenv('FLASK_ENV', 'dev')])
    else:
        app = Flask(__name__)
        app.config.from_object(config[app_environment])
    app.secret_key = 'xyzabc'
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
        return render_template('schedule.html', data=session['form_data'])
    
    @app.route('/summary', methods=('GET',))
    def summary():
        return render_template('summary.html', data=session['form_data'])

    return app



if __name__ == '__main__':
    create_app().run(debug=True)