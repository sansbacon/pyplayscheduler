# pyscheduler.py

import numpy as np

def calculate_byes(n_players, n_courts, n_rounds, players_per_court):
    """Calculates the byes
    
    Args:
        n_players (int): the total number of players
        n_courts (int): the total number of available courts per round
        n_rounds (int): the total number of rounds in the schedule
        players_per_court (int): the number of players per court
        
    Return:
        np.ndarray
        
    """
    # determine the number of needed byes
    # in large field, could need more than 1 bye per player
    # so create large list of byes and cut it down accordingly
    byes_per_round = n_players % 4 if n_players < (n_courts + 1) * players_per_court else n_players - (n_courts * players_per_court)
    byes_needed = byes_per_round * n_rounds
    return np.tile(np.arange(n_players), 5)[0:byes_needed].reshape(n_rounds, byes_per_round)


def cartesian(arrays, out=None):
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

    #m = n / arrays[0].size
    m = int(n / arrays[0].size) 
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m, 1:])
        for j in range(1, arrays[0].size):
        #for j in xrange(1, arrays[0].size):
            out[j*m:(j+1)*m, 1:] = out[0:m, 1:]
    return out


def dupcount(rng, byesched):
    """Counts duplicates in shuffled schedules"""
    # now shuffle the rounds
    idx = np.stack([rng.choice(range(byesched.shape[1]), byesched.shape[1], replace=False) for _ in range(byesched.shape[0])])
    shuff_sched = np.take_along_axis(byesched, idx, axis=1)

    # now count duplicate partners
    partners = shuff_sched.reshape(shuff_sched.shape[0] * shuff_sched.shape[1] // 2, 2)
    n_duplicates = partners.shape[0] - np.unique(partners, axis=0).shape[0]

    return {'iteration': idx, 'sched': shuff_sched, 'partners': partners, 'n_duplicates': n_duplicates}


def dupcount_improved(sched):
    """Improved version of dupcount
       Should not need to generate indices in a loop
       Can do it all at once
    """
    # now count duplicate partners
    partners = sched.reshape(sched.shape[0] * sched.shape[1] // 2, 2)
    return partners.shape[0] - np.unique(partners, axis=0).shape[0]
  
  
def oppdupcount(s):
    """Calculates opponent dupcount for schedule"""
    opponents = s.reshape(s.shape[0] * s.shape[1] // 4, 2, 2)
    opponents = np.array([cartesian(i) for i in opponents])
    opponents = opponents.reshape(opponents.shape[0] * opponents.shape[1], opponents.shape[2])
    return opponents.shape[0] - np.unique(opponents, axis=0).shape[0]    



