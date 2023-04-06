from collections import Counter, defaultdict
import itertools
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd


def opponent_summary(self, df: pd.DataFrame) -> Tuple[Counter, pd.DataFrame]:
    """Takes schedule_table df and creates summary of opponents

    Args:
        df(pd.DataFrame): dataframe created by schedule_table   
                        columns: n_players, n_rounds, n_courts, round, game, team1, team2 

    Returns:
        tuple of Counter, pd.DataFrame 
        columns: player, opponent, times

    Usage:
        >>> df = optimize_schedule(n_players=9, n_rounds=4, n_courts=2)
        >>> opponent_summary(df.query(q))
        
    """
    # part one: get the counts of tuples
    summ = defaultdict(int)
    for row in df.itertuples():
        for item in itertools.product(row.team1, row.team2):
            summ[tuple(sorted(item))] += 1
        
    # part two: convert to tabular format
    # show both sides of pairing for easier filtering
    # that is if 1 and 2 play together, have a row for 1, 2
    # and a row for 2, 1
    sched = [{'player': k[0], 'opponent': k[1], 'times': v}
            for k,v in summ.items()]
    sched += [{'player': k[1], 'opponent': k[0], 'times': v}
            for k,v in summ.items()]
    return Counter(summ.values()), pd.DataFrame(sched)

def partner_summary(df: pd.DataFrame) -> Tuple[Counter, pd.DataFrame]:
    """Takes schedule_table df and creates summary of partners

    Args:
        df(pd.DataFrame): dataframe created by schedule_table   
                          columns: n_players, n_rounds, n_courts, round, game, team1, team2 

    Returns:
        tuple of Counter, pd.DataFrame 
        columns: player, partner, times

    Usage:
        >>> df = optimize_schedule(n_players=9, n_rounds=4, n_courts=2)
        >>> partner_summary(df.query(q))
        
    """
    # part one: get the counts of tuples
    summ = defaultdict(int)
    for pairing in df.team1.values.tolist() + df.team2.values.tolist():
        summ[pairing] += 1
    
    # part two: convert to tabular format
    # show both sides of pairing for easier filtering
    # that is if 1 and 2 play together, have a row for 1, 2
    # and a row for 2, 1
    sched = [{'player': k[0], 'partner': k[1], 'times': v}
             for k,v in summ.items()]
    sched += [{'player': k[1], 'partner': k[0], 'times': v}
              for k,v in summ.items()]
    return Counter(summ.values()), pd.DataFrame(sched)


def readable_schedule(players: Union[np.ndarray, List[str]], schedule: np.ndarray) -> List[dict]:
    """Creates a readable schedule from a list of players and a schedule array
    
    Args:
        players(List[str]): the player names 
        schedule(np.ndarray): the schedule ndarray
    
    Returns:
        List[dict]

    """

    def _byes(players, round_schedule):
        """Creates array of strings from schedule"""
        return players[np.setdiff1d(np.arange(len(players)), round_schedule.flatten())]

    def _matchups(players, round_schedule):
        """Creates array of strings from schedule"""
        return [f'{players[item[0]]}-{players[item[1]]}\n{players[item[2]]}-{players[item[3]]}'
                for item in round_schedule]
            
    if not isinstance(players, np.ndarray):
        players = np.array(players)

    # schedule has keys for round, matchups, byes
    return [{'round': idx + 1, 'matchups': _matchups(players, round_schedule), 'byes': _byes(players, round_schedule)}
            for idx, round_schedule in enumerate(schedule)]

            
def schedule_table(d: Dict[Tuple[int, int, int], np.ndarray]) -> pd.DataFrame:
    """Converts a results dictionary into tabular format"""
    data = []
    for k, v in d.items():
        n_players, n_rounds, n_courts = k
        for idx, row in enumerate(v):
            for jdx, irow in enumerate(row):
                data.append({'n_players': n_players, 
                        'n_rounds': n_rounds, 
                        'n_courts': n_courts, 
                        'round': idx + 1,
                        'game': jdx + 1,
                        'team1': tuple(sorted(irow[0:2])),
                        'team2': tuple(sorted(irow[2:]))})
    return pd.DataFrame(data)

