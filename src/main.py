# app.py
# flask app to accept requests / serve schedule
import os

from pyscheduler import *
from flask import Flask, jsonify, request


app = Flask(__name__)



@app.route('/', methods=['POST'])
def schedule():
    """Sets schedule given values
       Request should be POST with json payload

    """
    data = request.get_json()
    n_players = int(data['n_players'])
    n_rounds = int(data['n_rounds'])
    n_courts = int(data['n_courts'])
    players_per_court = int(data['players_per_court'])
    iterations = int(data['iterations'])
        
    # get initial schedule - setdiff1d will remove shuffle so do shuffle later
    # sched is shape (n_rounds, n_players)
    sched = np.tile(np.arange(n_players), n_rounds).reshape(n_rounds, n_players)

    # remove the byes from the schedule
    # byesched is shape (n_rounds, n_players - byes_per_round)
    # so if 30 players, 8 rounds would be (8, 28)
    byes = calculate_byes(n_players, n_courts, n_rounds, players_per_court)
    byesched = np.array([np.setdiff1d(sched[i], byes[i]) for i in range(n_rounds)])

    # get randomized schedules
    # idx shape should be (iterations, n_rounds, n_players - byes_per_round)
    RNG = np.random.default_rng()
    idx = RNG.integers(0, byesched.shape[1] - 1, size=(iterations, n_rounds, byesched.shape[1])).argsort(axis=-1)
    scheds = np.take(byesched, idx)
    dupcounts = np.array([dupcount_improved(sched) for sched in scheds])

    # now judge opponents
    sched_idx = dupcounts == dupcounts.min()
    candidates = scheds[sched_idx]
    oppdupcounts = np.array([oppdupcount(s) for s in candidates])
    best = candidates[oppdupcounts.argmin()].reshape(n_rounds, n_courts, players_per_court)

    d = {'sched': best.tolist(), 'byes': byes.tolist(), 'dup_p': int(dupcounts.min()), 'dup_o': int(oppdupcounts.min())}       
    return jsonify(d)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
