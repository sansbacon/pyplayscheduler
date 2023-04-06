
import itertools
import random

import numpy as np
import pytest

from pyscheduler import Scheduler


@pytest.fixture
def s() -> Scheduler:
    params = {'n_players': 13, 'n_rounds': 10, 'n_courts': 3, 'iterations': 50}
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


def test_calculate_byes(player_names):
    """Tests correct shape of calculate_byes"""
    n_players = random.choice(range(13, 16))
    params = {'player_names': random.sample(player_names, n_players), 'n_rounds': 10, 'n_courts': 3, 'iterations': iterations}
    s = Scheduler(**params)
    byes = s.calculate_byes()
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


def test_counter_dups(sample_schedule, sample_dupcounts, tprint):
    params = {'n_players': 13, 'n_rounds': 5, 'n_courts': 3, 'iterations': 5}
    s = Scheduler(**params)
    cdupes = np.array([s.counter_dups(sched, 'partner') for sched in sample_schedule])
    assert np.array_equal(sample_dupcounts, cdupes), 'Arrays should be equal'


    """
    
    
    def counter_dups(self, sched: np.ndarray, dup_type: str, return_data: bool = False) -> int:
        
        Args:
            sched(np.ndarray): the schedule to count the duplicates
            dup_type(str): the dupes to count (opponent or partner)
            return_data(bool): whether to return underlying data, default False

        Returns:
            int

    
    def dupcount(self, sched: np.ndarray, return_data: bool = False) -> int:
    
        Args:
            sched(np.ndarray): the schedule to count the duplicates
            return_data(bool): whether to return underlying data, default False

        Returns:
            np.ndarray

    
            
    def dupcount_weighted(self, sched: np.ndarray, weights: np.ndarray = None) -> int:
        
        Args:
            sched(np.ndarray): the schedule to count the duplicates
            weights(np.ndarray): the weights to apply to duplicate counts

        Returns:
            int

        
    def oppdupcount(self, sched: np.ndarray, return_data: bool = False) -> int:
        
        Args:
            sched(np.ndarray): the schedule to count the duplicates
            return_data(bool): whether to return underlying data, default False

        Returns:
            np.ndarray

    
    def oppdupcount_weighted(self, sched: np.ndarray, weights: np.ndarray = None) -> int:
        
        Args:
            sched(np.ndarray): the schedule to count the duplicates
            weights(np.ndarray): the weights to apply to duplicate counts

        Returns:
            int

    
    def optimize_schedule(
            self,
            n_players: int, 
            n_rounds: int, 
            n_courts: int, 
            iterations: int = 10000, 
            players_per_court: int = 4,
            scoring_function: str = 'naive') -> np.ndarray:
        
        Args:
            n_players(int): total number of players in pool
            n_rounds(int): number of rounds of play
            n_courts(int): number of courts to use
            iterations(int): number of iterations to optimize on, default 10000
            players_per_court(int): default 4
            scoring_function(str): specifies how to score optimality of schedule, default 'naive'

        Returns:
            np.ndarray
       

    @staticmethod
    def shuffle_along(X):
        [np.random.shuffle(x) for x in X]
"""