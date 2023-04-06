# pyplayscheduler
Handles play schedules with byes - minimizes duplicate partners and opponents

# Usage

```
from pyplayscheduler import Scheduler

player_names = ['Joe', 'Tom', 'Steve', 'Bill', 'Sharon', 'Jill', 'Betty', 'Birdie', 'Sheila']
s = Scheduler(player_names=player_names, n_courts=2, n_rounds=5)
s.optimize_schedule()
```