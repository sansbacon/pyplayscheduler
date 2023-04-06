# pyscheduler/scheduler.py

from collections import Counter
import logging
import random
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from pyscheduler.helper import *
from pyscheduler.scheduler import Scheduler


class ScheduleSearch:
    """"Class for researching schedule options for a variety of parameters
    
    Usage:
        player_names = ['Joe', 'Tom', 'Steve', 'Bill', 'Tammy', 'Stevie', 'James', 'Jamie', 'Shawn']
        s = Scheduler(player_names, n_rounds=5, n_courts=2, iterations=1000)
        s.optimize_schedule()

    """
    def __init__(self, 
                 player_names: List[str], 
                 n_rounds: int, 
                 n_courts: int, 
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
        self.player_names = player_names if isinstance(player_names, np.ndarray) else np.array(player_names)
        self.RNG = np.random.default_rng()
        self.n_courts = n_courts
        self.n_rounds = n_rounds
        self.players_per_court = players_per_court
        self.iterations = iterations

    def generate_optimals(
            self,
            n_players_range: tuple = (9, 26), 
            n_rounds_range: tuple = (4, 13), 
            n_courts_range: tuple = (2, 9),
            results: dict = None,
            players_per_court: int = 4
        ) -> Dict[Tuple[int, int, int], np.ndarray]:
        """Generates optimal schedules for a variety of combinations
        
        Args:
            n_players_range(tuple): default (9, 26)
            n_rounds_range(tuple): default (4, 13)
            n_courts_range(tuple): default (2, 9)
            results(dict): default None, allows reuse of prior runs without duplication
            players_per_court(int): default 4
        
        Returns:
            dict
            key is 3-tuple of n_players, n_rounds, n_courts, value is np.ndarray

        """
        if not results:
            results = {}

        for n_players in range(*n_players_range):
            for n_rounds in range(*n_rounds_range):
                for n_courts in range(*n_courts_range):
                    if results.get((n_players, n_rounds, n_courts)) is None:
                        logging.info(f'Starting {n_players}-{n_rounds}-{n_courts}')
                        try:
                            if n_players // players_per_court >= n_courts:
                                s = Scheduler(None, n_rounds, n_courts)
                                results[(n_players, n_rounds, n_courts)] = s.optimize_schedule()
                        except ValueError as e:
                            logging.exception(e)
        return results


    def optimization_trials(
            self,
            n_players: int, 
            n_rounds: int, 
            n_courts: int, 
            trials: int = 500, 
            iterations: int = 10000, 
            players_per_court: int = 4
        ) -> pd.DataFrame:
        """Runs n trials to optimizes schedule for given parameters
        
        Args:
            n_players(int): total number of players in pool
            n_rounds(int): number of rounds of play
            n_courts(int): number of courts to use
            trials(int): number of trials to run, default 500
            iterations(int): number of iterations per trial to optimize on, default 10000
            players_per_court(int): default 4

        Returns:
            tuple
            pd.DataFrame, Dict[int, pd.DataFrame], Dict[int, pd.DataFrame]

        """    
        trial_results = []
        psumms = {}
        osumms = {}

        for i in range(1, trials + 1):
            s = Scheduler(None, n_rounds, n_courts, iterations=iterations, players_per_court=players_per_court)
            sched = {(n_players, n_rounds, n_courts): s.optimize_schedule()}
            df = schedule_table(sched)
            pcounts, psumm = partner_summary(df)
            psumms[i] = psumm
            for k, v in pcounts.items():
                result = {'trial': i, 'count_type': 'partner', 'count_value': k, 'count_count': v}
                trial_results.append(result)
            ocounts, osumm = opponent_summary(df)
            osumms[i] = osumm
            for k, v in ocounts.items():
                result = {'trial': i, 'count_type': 'opponent', 'count_value': k, 'count_count': v}
                trial_results.append(result)

        return pd.DataFrame(trial_results), psumms, osumms


    def _trial(i, n_players, n_rounds, n_courts, max_trials, max_iterations, **kwargs):
        trials = int(random.random() * max_trials)
        iterations = int(random.random() * max_iterations)
        return {
            'tt': i,
            'n_players': n_players, 
            'n_rounds': n_rounds, 
            'n_courts': n_courts, 
            'max_trials': max_trials,
            'max_iterations': max_iterations,
            'trials': trials,
            'iterations': iterations,
            'results': optimization_trials(n_players, n_rounds, n_courts, trials, iterations)
        }


    def trials_of_trials(n_players: int, 
                        n_rounds: int, 
                        n_courts: int,
                        max_trials: int = 10,
                        max_iterations: int = 1000,
                        max_tt: int = 50) -> List[Tuple]:
        """Tests out different combinations of trial parameters"""
        with Manager() as manager:
            with manager.Pool() as p:
                wanted = ['n_players', 'n_rounds', 'n_courts', 'max_trials', 'max_iterations']
                args = {k: v for k, v in locals().items() if k in wanted}
                return p.map(functools.partial(_trial, **args), range(1, max_tt + 1))