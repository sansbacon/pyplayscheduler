from flask import Blueprint, render_template, session, redirect, request, url_for, current_app
from forms import SettingsForm
from helper import readable_schedule, schedule_summary


blueprint = Blueprint('blueprint', __name__, static_folder='static')


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
            'players': [str(i) for i in form.players.data.split('\n')], 
            'rounds': form.rounds.data, 
            'courts': form.courts.data
        }
        return redirect(url_for('blueprint.schedule'))
    return render_template('index.html', form=form)


@blueprint.route('/schedule', methods=('GET',))
def schedule():
    try:
        f = session['form_data']
        sched = current_app.schedule.get((int(f['courts']), int(f['rounds']), len(f['players'])))
        rs = readable_schedule(f['players'], sched)
    except:
        rs = [[1, 1, 'No available schedule', 'Please try again']]
    data = {**f, **{'schedule': rs}}
    print(data)
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

