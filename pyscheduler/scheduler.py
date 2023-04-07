# pyscheduler/scheduler.py

from collections import Counter
from dataclasses import dataclass
import logging
from typing import List

import numpy as np


@dataclass
class Schedule:
    """Class for encapsulating a single schedule
    
    n_players: int = None
    players_per_court: int = 4
    schedule: np.ndarray = None
    partner_dupcount: float = None
    opponent_dupcount: float = None
    player_names: List[str] = None
    
    """
    n_players: int = None
    players_per_court: int = 4
    schedule: np.ndarray = None
    partner_dupcount: float = None
    opponent_dupcount: float = None
    player_names: List[str] = None
    
    @property
    def n_rounds(self):
        return self.schedule.shape[0]

    @property
    def n_courts(self):
        return self.schedule.shape[1] // self.players_per_court

    @property
    def player_count(self):
        return np.unique(self.schedule.flatten()).shape[0]

    def to_dict(self):
        """Converts object to three-keyed dict: schedule, partner_dupcount, opponent_dupcount"""
        return {
            'schedule': self.schedule,
            'partner_dupcount': self.partner_dupcount,
            'opponent_dupcount': self.opponent_dupcount            
        }


class Scheduler:
    """"Class for generating optimal round-robin / open play schedule
    
    Usage:
        player_names = ['Joe', 'Tom', 'Steve', 'Bill', 'Tammy', 'Stevie', 'James', 'Jamie', 'Shawn']
        s = Scheduler(player_names, n_rounds=5, n_courts=2, iterations=1000)
        s.optimize_schedule()

    """
    def __init__(self, 
                 n_rounds: int, 
                 n_courts: int, 
                 n_players: int = None,
                 player_names: List[str] = None, 
                 players_per_court: int = 4, 
                 iterations: int = 500):
        """Instantiate Scheduler object
        
        Args:
            player_names(List[str]): the player names
            n_rounds(int): number of play rounds
            n_courts(int): number of courts to use
            players_per_court(int): default 4
            iterations(int): the number of schedules to draw optimal from

        Returns:
            Scheduler

        """
        logging.getLogger(__name__).addHandler(logging.NullHandler)

        # need player names or number of players
        if player_names is not None:
            if type(player_names) not in [list, np.ndarray]:
                raise ValueError(f'Invalid value (must be list or array) for player_names: {player_names}')
            self.player_names = player_names if isinstance(player_names, np.ndarray) else np.array(player_names)
            self._n_players = self.player_names.shape[0]
        elif n_players is not None:
            self.player_names = []
            self._n_players = n_players
        else:
            raise ValueError('Must specify player names or number of players')
        self.n_courts = n_courts
        self.n_rounds = n_rounds
        self.players_per_court = players_per_court
        self.iterations = iterations
        self.optimal_schedule = None

    @property
    def n_players(self):
        if self._n_players:
            return self._n_players
        return self.player_names.shape[0]

    def create_schedules(self, 
                         n_players: int = None, 
                         n_rounds: int = None, 
                         n_courts: int = None, 
                         iterations: int = None, 
                         players_per_court: int = None) -> np.ndarray:
        """Creates array of schedules
        
        Args:
            n_players(int): the total number of players in the pool
            n_rounds(int): number of play rounds
            n_courts(int): number of courts to use
            iterations(int): the number of schedules to draw optimal from
            players_per_court(int): default 4
        
        Returns:
            np.ndarray

        """
        # use instance attributes unless overridden
        n_players = n_players if n_players else self.n_players
        n_courts = n_courts if n_courts else self.n_courts
        n_rounds = n_rounds if n_rounds else self.n_rounds
        players_per_court = players_per_court if players_per_court else self.players_per_court
        iterations = iterations if iterations else self.iterations
        
        # create 2d aray byeschedule (iterations * n_rounds, n_courts * players_per_court)
        # then shuffle each row inplace using shuffle_along
        # after shuffle, can reshape to 3d array (iterations, n_rounds, n_courts * players_per_court)
        sched = np.tile(np.arange(n_players), n_rounds).reshape(n_rounds, n_players)
        byes = self.calculate_byes(n_players, n_courts, n_rounds, players_per_court)
        byesched = np.tile(np.array([np.setdiff1d(sched[i], byes[i]) for i in range(n_rounds)]), (iterations, 1, 1)).reshape(iterations * n_rounds, players_per_court * n_courts)
        self.shuffle_along(byesched)
        return byesched.reshape(iterations, n_rounds, n_courts * players_per_court)

    def calculate_byes(self, 
                       n_players: int = None, 
                       n_courts: int = None, 
                       n_rounds: int = None, 
                       players_per_court: int = None) -> np.ndarray:
        """Calculates the byes
        
        Args:
            n_players (int): the total number of players
            n_courts (int): the total number of available courts per round
            n_rounds (int): the total number of rounds in the schedule
            players_per_court (int): the number of players per court
            
        Return:
            np.ndarray
            
        """
        # process function arguments
        n_players = n_players if n_players else self.n_players
        n_courts = n_courts if n_courts else self.n_courts
        n_rounds = n_rounds if n_rounds else self.n_rounds
        players_per_court = players_per_court if players_per_court else self.players_per_court

        # determine the number of needed byes
        # in large field, could need more than 1 bye per player
        # so create large list of byes and cut it down accordingly
        byes_per_round = n_players % 4 if n_players < (n_courts + 1) * players_per_court else n_players - (n_courts * players_per_court)
        byes_needed = byes_per_round * n_rounds
        return np.tile(np.arange(n_players), 5)[0:byes_needed].reshape(n_rounds, byes_per_round)

    def cartesian(self, arrays: np.ndarray, out=None) -> np.ndarray:
        """Generate a cartesian product of input arrays.

        Args:
            arrays (list of array-like): 1-D arrays to form the cartesian product of.

        Returns: 
            np.ndarray of shape (M, len(arrays))

        """
        arrays = [np.asarray(x) for x in arrays]
        dtype = arrays[0].dtype

        n = np.prod([x.size for x in arrays])
        if out is None:
            out = np.zeros([n, len(arrays)], dtype=dtype)

        m = int(n / arrays[0].size) 
        out[:,0] = np.repeat(arrays[0], m)
        if arrays[1:]:
            self.cartesian(arrays[1:], out=out[0:m, 1:])
            for j in range(1, arrays[0].size):
                out[j*m:(j+1)*m, 1:] = out[0:m, 1:]
        return out

    def counter_dups(self, sched: np.ndarray, dup_type: str, return_data: bool = False) -> int:
        """Uses counter to calculate duplicates
        
        Args:
            sched(np.ndarray): the schedule to count the duplicates
            dup_type(str): the dupes to count (opponent or partner)
            return_data(bool): whether to return underlying data, default False

        Returns:
            int

        """
        if dup_type == 'partner':
            expected_shape = tuple([(self.n_courts * self.n_rounds * self.players_per_court) // 2, 2])
        elif dup_type == 'opponent':
            expected_shape = tuple([(self.n_courts * self.n_rounds * self.players_per_court), 2])
        sched = sched.reshape(*expected_shape)
        c = Counter(tuple(sorted(i)) for i in sched)
        dupes = sum([(k - 1) * v for k, v in Counter(c.values()).items()]) 
        if return_data:
            return dupes, c
        return dupes

    def dupcount(self, sched: np.ndarray, return_data: bool = False) -> int:
        """Counts duplicate partners in a schedule

        Args:
            sched(np.ndarray): the schedule to count the duplicates
            return_data(bool): whether to return underlying data, default False

        Returns:
            np.ndarray

        """
        # now count duplicate partners
        # partners is 3d array of (iterations, n_rounds * n_courts * players_per_court, players_per_court / 2)
        # if 5 iterations, 5 rounds, 3 courts, 4 players per court
        # shape should be 5, 60, 2
        partners = sched.reshape(sched.shape[0] * sched.shape[1] // 2, 2)
        sortidx = np.argsort(partners, axis=1)
        dupcount = partners.shape[0] - np.unique(partners[np.arange(partners.shape[0])[:,None], sortidx], axis=0).shape[0]
        if return_data:
            return dupcount, partners
        return dupcount

    def dupcount_weighted(self, sched: np.ndarray, weights: np.ndarray = None) -> int:
        """Counts duplicate partners in a schedule

        Args:
            sched(np.ndarray): the schedule to count the duplicates
            weights(np.ndarray): the weights to apply to duplicate counts

        Returns:
            int

        """
        c = Counter([tuple(sorted(i)) for i in sched.reshape(sched.shape[0] * sched.shape[1] // 2, 2)])
        n = max(c.values()) + 1
        dupecount = np.zeros(n)
        if weights is None:
            weights = np.ones(n) + np.arange(0, .1 * n, .1)
        for k, v in Counter(c.values()).items():
            dupecount[k] = v 
        return np.sum(dupecount * weights)

    def oppdupcount(self, sched: np.ndarray, return_data: bool = False) -> int:
        """Calculates opponent dupcount for single schedule (with 1+ rounds)
        
        Args:
            sched(np.ndarray): the schedule to count the duplicates
            return_data(bool): whether to return underlying data, default False

        Returns:
            np.ndarray

        """
        ppc = self.players_per_court
        
        # step 1: have to convert schedule into pairs of player-opponent
        # the total number should be n_rounds * n_courts * players_per_court
        opponents = np.array([self.cartesian(i) for i in 
                              sched.reshape((sched.shape[0] * sched.shape[1]) // ppc, ppc // 2, ppc // 2)])

        # step 2: need to reshape and sort the 2-element arrays because we are going to count tuples
        expected_shape = self.n_rounds * self.n_courts, ppc, ppc // 2
        assert opponents.shape == expected_shape, f'Expected {expected_shape}, got {opponents.shape}'
        opponents = opponents.reshape(self.n_rounds * self.n_courts * ppc, ppc // 2)
        opponents = np.sort(opponents, axis=-1)

        # step 3: return the dupcount and optional data 
        dupcount = opponents.shape[0] - np.unique(opponents, axis=0).shape[0]   
        if return_data:
            return dupcount, opponents
        return dupcount

    def oppdupcount_weighted(self, sched: np.ndarray, weights: np.ndarray = None) -> int:
        """Calculates weighted opponent dupcount for single schedule (with 1+ rounds)
        
        Args:
            sched(np.ndarray): the schedule to count the duplicates
            weights(np.ndarray): the weights to apply to duplicate counts

        Returns:
            int

        """
        ppc = self.players_per_court
        
        # step 1: have to convert schedule into pairs of player-opponent
        # the total number should be n_rounds * n_courts * players_per_court
        opponents = np.array([self.cartesian(i) for i in 
                              sched.reshape(sched.shape[0] * sched.shape[1] // ppc, ppc // 2, ppc // 2)])

        # step 2: need to reshape and sort the 2-element arrays because we are going to count tuples
        opponents = np.sort(opponents.reshape(self.n_rounds * self.n_courts * ppc, 2), axis=-1)

        # step 3: weighted counts
        c = Counter([tuple(i) for i in sched])
        n = max(c.values()) + 1
        dupecount = np.zeros(n)
        if weights is None:
            weights = np.ones(n) + np.arange(0, .1 * n, .1)
        for k, v in Counter(c.values()).items():
            dupecount[k] = v 
        return n
    
    def optimize_schedule(
            self,
            n_players: int = None, 
            n_rounds: int = None, 
            n_courts: int = None, 
            iterations: int = None, 
            players_per_court: int = None,
            scoring_function: str = 'naive') -> Schedule:
        """Optimizes schedule for given parameters
        
        Args:
            n_players(int): total number of players in pool
            n_rounds(int): number of rounds of play
            n_courts(int): number of courts to use
            iterations(int): number of iterations to optimize on, default 10000
            players_per_court(int): default 4
            scoring_function(str): specifies how to score optimality of schedule, default 'naive'

        Returns:
            Schedule

        """    
        # process function arguments
        iterations = iterations if iterations else self.iterations
        n_players = n_players if n_players else self.n_players
        n_courts = n_courts if n_courts else self.n_courts
        n_rounds = n_rounds if n_rounds else self.n_rounds
        players_per_court = players_per_court if players_per_court else self.players_per_court

        # get initial schedule - setdiff1d will remove shuffle so do shuffle later
        # sched is shape (n_rounds, n_players)
        scheds = self.create_schedules(n_players, n_rounds, n_courts, iterations, players_per_court)

        # for naive scoring function, we first minimize the count of duplicates
        # from the 1+ schedules with the same duplicate count, we then minimize opponent duplicates
        if scoring_function == 'naive':
            dupcounts = np.array([self.dupcount(sched) for sched in scheds])
            sched_idx = dupcounts == dupcounts.min()
            candidates = scheds[sched_idx]
            oppdupcounts = np.array([self.oppdupcount(s) for s in candidates])
            optimal = candidates[oppdupcounts.argmin()].reshape(n_rounds, n_courts, players_per_court)

        # for weighted scoring function, we put a penalty on higher duplicate numbers (3+)
        # we also try to balance partner and opponent duplicates more
        if scoring_function == 'weighted':
            dupcounts = np.array([self.dupcount_weighted(sched) for sched in scheds])
            oppdupcounts = np.array([self.dupcount_weighted(sched) for sched in scheds])
            sched_idx = dupcounts == dupcounts.min()
            candidates = scheds[sched_idx]
            oppdupcounts = np.array([self.oppdupcount(s) for s in candidates])
            optimal = candidates[oppdupcounts.argmin()].reshape(n_rounds, n_courts, players_per_court)

        return Schedule(schedule=optimal, partner_dupcount=dupcounts.min(), opponent_dupcount=oppdupcounts.min())

    @staticmethod
    def shuffle_along(X):
        """Minimal in place independent-row shuffler."""
        [np.random.shuffle(x) for x in X]