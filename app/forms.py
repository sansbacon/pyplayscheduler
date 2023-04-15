from flask_wtf import FlaskForm
from wtforms import TimeField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired

from helper import get_timestamp, number_to_word


class SettingsForm(FlaskForm):
    players = TextAreaField('Players', render_kw={"rows": 15, "cols": 1}, validators=[DataRequired()])
    courts = SelectField('Courts', choices=[(i, number_to_word(str(i))) for i in range(1, 13)], default=3)
    rounds = SelectField('Rounds', choices=[(i, number_to_word(str(i))) for i in range(1, 13)], default=8)
    start_time = TimeField('Start Time', format='%H:%M', default=get_timestamp())
    round_time = SelectField('Minutes Per Round', choices=[(str(i), number_to_word(str(i))) for i in range(5, 35, 5)], default=15)
    submit = SubmitField('Create Schedule')


