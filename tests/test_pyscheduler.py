import numpy as np
import pytest

from pyscheduler import Scheduler


def test_scheduler(player_names):
    assert Scheduler(player_names, 5, 5)