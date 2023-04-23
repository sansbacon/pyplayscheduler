from collections import defaultdict
import datetime
import json
import itertools
import re
from typing import Any, Dict, List, Tuple

import numpy as np
from pyscheduler import Scheduler

from model import OptimalSchedule


def create_optimal(**kwargs) -> dict:
    """Creates optimal schedule given parameters"""
    s = Scheduler(**kwargs)
    sched = s.optimize_schedule()
    d = sched.to_dict()
    sched = d.get('schedule')
    return OptimalSchedule(schedule=sched.tolist(), **kwargs)


def create_schedule_key(*args):
    """Creates a schedule key"""
    return '_'.join(['schedule'] + [str(arg) for arg in args])


def get_timestamp() -> datetime.datetime:
    today = datetime.datetime.now()
    return datetime.datetime(today.year, today.month, today.day, 19, 0, 0)


def number_to_word(n: Any) -> str:
        return {'1': "One", '2': "Two", '3': "Three", '4': "Four", '5': "Five", '6': "Six",
                '7': "Seven", '8': "Eight", '9': "Nine", '10': "Ten", '11': "Eleven", '12': "Twelve",
                '13': "Thirteen", '14': "Fourteen", '15': "Fifteen", '20': "Twenty", '25': "Twenty-Five", '30': 'Thirty'}.get(str(n))


def parse_players(s, sep='\n'):
    if sep == '\n':
        return [str(i).strip() for i in re.split(r'[\n\r]+', s) if re.search(r'\w+', i)]


def readable_schedule(players: list, sched: str, sep=' - ') -> List[List]:
    """Creates readable schedule"""
    # data has players and schedule keys
    if not sched:
        return [[1, 1, 'No available schedule', 'No available schedule']]
    if isinstance(sched, str):
        sched = json.loads(sched)
    items = []
    for idx, rnd in enumerate(sched):
        for court, matchup in enumerate(rnd):
            team1 = sep.join([players[int(i)].strip() for i in matchup[0:2]])
            team2 = sep.join([players[int(i)].strip() for i in matchup[2:]])            
            items.append([idx + 1, court + 1, team1, team2])
    return items


def schedule_summary(players: List[str], sched: Any) -> Tuple[Dict[str, Any], Dict[str, Any]]:
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
    if isinstance(sched, str):
        sched = json.loads(sched)
    if isinstance(sched, np.ndarray):
        sched = sched.tolist()
        
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

    dup_partners = {idx: 0 for idx in range(len(players))}
    dup_opponents = {idx: 0 for idx in range(len(players))}
    
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
        
    return ({players[k]: v for k, v in dup_partners.items()}, 
            {players[k]: v for k, v in dup_opponents.items()})


def test_summ():
    """Tests the summary schedule"""
    sched = json.dumps([[[1, 2, 3, 4], [5, 6, 7, 8]], [[2, 1, 4, 3], [6, 7, 5, 8]]])
    r = schedule_summary(list(range(1, 9)), sched)
    assert r['dup_opponents'] == {1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 1, 7: 1, 8: 1}, r['dup_opponents']
    assert r['dup_partners'] == {1: 1, 2: 1, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0, 8: 0}, r['dup_partners']
    print('Tests passed!')


def ts():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    
if __name__ == '__main__':
    test_summ()