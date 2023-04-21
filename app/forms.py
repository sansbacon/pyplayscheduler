# pyplayscheduler/app/forms.py

import re

from flask_wtf import FlaskForm
from wtforms import TimeField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError

from helper import number_to_word


class SettingsForm(FlaskForm):
    courts = SelectField('Courts', choices=[(i, number_to_word(str(i))) for i in range(1, 13)])
    rounds = SelectField('Rounds', choices=[(i, number_to_word(str(i))) for i in range(1, 13)])
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


