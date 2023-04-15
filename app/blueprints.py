from flask import Blueprint, render_template, session, redirect, url_for, current_app
from forms import SettingsForm
from helper import readable_schedule, schedule_summary


blueprint = Blueprint('blueprint', __name__, static_folder='static')


@blueprint.route('/', methods=('GET', 'POST'))
def index():
    form = SettingsForm(meta={'csrf': False})
    if form.validate_on_submit():
        session['form_data'] = {
            'players': [str(i) for i in form.players.data.split('\n')], 
            'rounds': form.rounds.data, 
            'courts': form.courts.data
        }
        return redirect(url_for('blueprint.schedule'))
    return render_template('index.html', form=form)


@blueprint.route('/schedule', methods=('GET',))
def schedule():
    f = session['form_data']
    sched = current_app.schedule.get((int(f['courts']), int(f['rounds']), len(f['players'])))
    session['form_data']['schedule'] = sched
    rs = readable_schedule(f['players'], sched)
    data = {**f, **{'schedule': rs}}
    return render_template('schedule.html', data=data)


@blueprint.route('/summary', methods=('GET',))
def summary():
    f = session['form_data']
    players = f['players']
    schedule = f.get('schedule', current_app.schedule.get((int(f['courts']), int(f['rounds']), len(players))))
    partners, opponents = schedule_summary(players, schedule)
    data = {'summary': []}

    for (k, v), (k2, v2) in zip(partners.items(), opponents.items()):
        data['summary'].append([k, v, v2])       

    return render_template('summary.html', data=data)

