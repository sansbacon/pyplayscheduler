
import itertools
import random

import numpy as np
import pytest

from pyscheduler import Scheduler


@pytest.fixture
def s() -> Scheduler:
    params = {'n_players': 13, 'n_rounds': 5, 'n_courts': 3, 'iterations': 50}
    return Scheduler(**params)
    

def test_scheduler_valid(player_names):
    """Tests constructor"""
    params = {'n_players': 13, 'n_rounds': 5, 'n_courts': 3}
    assert Scheduler(**params)

    params = {'player_names': player_names, 'n_rounds': 5, 'n_courts': 3}
    assert Scheduler(**params)

    params = {'player_names': np.array(player_names), 'n_rounds': 5, 'n_courts': 3}
    assert Scheduler(**params)


def test_scheduler_invalid():
    """Tests constructor with invalid parameters"""
    with pytest.raises(TypeError):
        Scheduler()

    with pytest.raises(ValueError):
        Scheduler(player_names='Joe', **{'n_players': 13, 'n_rounds': 5, 'n_courts': 3})

    with pytest.raises(ValueError):
        Scheduler(player_names=1, **{'n_players': 13, 'n_rounds': 5, 'n_courts': 3})

    with pytest.raises(ValueError):
        Scheduler(**{'n_rounds': 5, 'n_courts': 5})


def test_n_players(player_names):
    """Tests player_names property"""
    n_players = len(player_names)
    params = {'n_players': n_players, 'n_rounds': 5, 'n_courts': 3}
    s = Scheduler(**params)
    assert s.n_players == n_players

    params = {'player_names': player_names, 'n_rounds': 5, 'n_courts': 3}
    s = Scheduler(**params)
    assert s.n_players == n_players

    idx = 5
    params = {'n_players': n_players, 'player_names': player_names[0:idx], 'n_rounds': 5, 'n_courts': 3}
    s = Scheduler(**params)
    assert s.n_players == idx


def test_create_schedules(s: Scheduler):
    """Tests that schedule has correct shape given parameters"""    
    scheds = s.create_schedules()
    assert scheds.shape == (s.iterations, s.n_rounds, s.n_courts * s.players_per_court)    


def test_calculate_byes(player_names, tprint):
    """Tests correct shape of calculate_byes"""
    n_players = random.choice(range(13, 16))
    iterations = 50
    params = {'n_players': n_players, 'n_rounds': 12, 'n_courts': 3, 'iterations': iterations}
    s = Scheduler(**params)
    byes = s.calculate_byes()
    tprint(byes)
    assert byes.shape == (s.n_rounds, n_players - (s.n_courts * s.players_per_court))    
    assert set(byes.flatten()) == set(range(n_players))


def test_cartesian():
    """Tests the cartesian method"""
    a = [1, 2, 3]
    b = [4, 5, 6]
    params = {'n_players': 13, 'n_rounds': 10, 'n_courts': 3, 'iterations': 50}
    s = Scheduler(**params)
    c = {tuple(i) for i in s.cartesian([a, b])}
    c2 = {i for i in itertools.product(a, b)}
    assert c == c2, f'Combinations do not match: {c} {c2}'


def test_counter_dups_partner(sample_schedule, sample_dupcounts):
    params = {'n_players': 13, 'n_rounds': 5, 'n_courts': 3, 'iterations': 5}
    s = Scheduler(**params)
    cdupes = np.array([s.counter_dups(sched, 'partner') for sched in sample_schedule])
    assert np.array_equal(sample_dupcounts, cdupes), 'Arrays should be equal'


def test_counter_dups_opponent(sample_schedule: np.ndarray, sample_dupcounts_opp: np.ndarray):
    """Tests counter_dups with opponent parameter"""
    params = {'n_players': 13, 'n_rounds': 5, 'n_courts': 3, 'iterations': 5}
    s = Scheduler(**params)
    dupcounts = []
    
    for sched in sample_schedule:
        ppc = s.players_per_court
        opponents = np.array([s.cartesian(i) for i in 
                              sched.reshape(sched.shape[0] * sched.shape[1] // ppc, ppc // 2, ppc // 2)])
        opponents = np.sort(opponents.reshape(s.n_rounds * s.n_courts * ppc, 2), axis=-1)
        dupcounts.append(s.counter_dups(opponents, 'opponent'))
    assert np.array_equal(sample_dupcounts_opp, np.array(dupcounts)), 'Arrays should be equal'


def test_dupcount(s: Scheduler, sample_schedule: np.ndarray, sample_dupcounts: np.ndarray):
    """Tests dupcount method"""
    dups = np.array([s.dupcount(sched) for sched in sample_schedule])
    assert np.array_equal(dups, sample_dupcounts)


def test_oppdupcount(s: Scheduler, sample_schedule: np.ndarray, sample_dupcounts_opp: np.ndarray, tprint):
    """Tests oppdupcount method"""
    dups = np.array([s.oppdupcount(sched) for sched in sample_schedule])
    assert np.array_equal(dups, sample_dupcounts_opp)


def test_dupcount_weighted(s:Scheduler, sample_schedule: np.ndarray, sample_dupcounts_weighted: np.ndarray):
    """Tests weighted dupcounts"""
    # def dupcount_weighted(self, sched: np.ndarray, weights: np.ndarray = None) -> int:
    pass


def test_oppdupcount_weighted(s:Scheduler, sample_schedule: np.ndarray, sample_dupcounts_opp_weighted: np.ndarray):
    """Tests weighted dupcounts"""
    # def dupcount_weighted(self, sched: np.ndarray, weights: np.ndarray = None) -> int:
    pass


def test_optimize_schedule(s: Scheduler):
    expected_shape = (s.n_rounds, s.n_courts, s.players_per_court)
    sched = s.optimize_schedule()
    assert sched.schedule.shape == expected_shape


def test_shuffle_along(s: Scheduler):
    """Tests shuffle along method"""
    failures = 0
    for i in range(1000):
        n = 12
        a = np.arange(0, n).reshape(n // 4, 4)
        b = np.arange(0, n).reshape(n // 4, 4)
        assert np.array_equal(a, b)
        s.shuffle_along(a)
        if np.array_equal(a, b):
            failures += 1
    assert failures < 2