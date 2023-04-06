# pyplayscheduler/tests/conftest.py
# -*- coding: utf-8 -*-
# Copyright (C) 2023 Eric Truett

from pathlib import Path
import sys

import numpy as np
import pytest


sys.path.append("../pyscheduler")


@pytest.fixture(scope="session", autouse=True)
def root_directory(request):
    """Gets root directory"""
    return Path(request.config.rootdir)


@pytest.fixture(scope="session", autouse=True)
def test_directory(request):
    """Gets root directory of tests"""
    return Path(request.config.rootdir) / "tests"


@pytest.fixture()
def tprint(request, capsys):
    """Fixture for printing info after test, not supressed by pytest stdout/stderr capture"""
    lines = []
    yield lines.append

    with capsys.disabled():
        for line in lines:
            sys.stdout.write("\n{}".format(line))


@pytest.fixture()
def player_names():
    return [
        'Olivia', 'Emma', 'Charlotte', 'Amelia', 'Ava', 'Sophia', 'Isabella', 
        'Noah', 'Oliver', 'Elijah', 'James', 'William', 'Benjamin', 'Eric', 'Eva',
        'Chuck', 'Courtney', 'Natalie', 'Liz', 'Bill', 'Audrey', 'Jerry', 'Chase', 'Bobby',
        'Ian', 'Kerry', 'Jeff', 'Mark', 'Ansel', 'Bob', 'Justin', 'Ben', 'Colin', 'Lucy', 'Callie',
        'Stevie', 'Lucas', 'JW', 'JR', 'JJ', 'Podfather', 'Konami', 'Callan', 'Kellen', 'Sarah', 'Shelly',
        'Matt', 'Patrick', 'Jay', 'Tyson', 'Etta', 'Meghan', 'Catherine', 'Kathy', 'Katie', 'Annie', 'Anna',
        'Ace', 'Scottie', 'Scooter', 'Brad', 'Brian', 'Bradley', 'Benjy', 'Harry', 'Harriett', 'Maddie', 'Matty'
    ]

@pytest.fixture()
def sample_schedule():
    return np.array(
        [[[ 2,  9,  1, 11,  7,  6,  4, 12, 10,  5,  3,  8],
          [11,  0,  2,  9,  6,  5,  8,  3, 12,  4, 10,  7],
          [12,  7,  1, 10,  9,  4,  6,  0, 11,  5,  3,  8],
          [10,  1,  9,  5,  7,  4,  2, 12,  6, 11,  8,  0],
          [ 6,  7,  5, 10,  3,  9,  1,  0,  8, 12,  2, 11]],

        [[ 3,  6, 12, 10,  7,  8,  1,  2,  9,  5, 11,  4],
            [ 9,  4,  3, 11,  8, 10,  2,  0,  7, 12,  5,  6],
            [ 4, 11,  6,  5,  7, 10,  9,  8, 12,  0,  1,  3],
            [12, 10, 11,  7,  4,  5,  0,  1,  8,  2,  6,  9],
            [11,  8,  1,  9,  6,  2,  0, 12,  7, 10,  3,  5]],

        [[ 5, 12,  9, 10,  6,  1,  7,  3,  2,  8,  4, 11],
            [ 4, 12,  5,  3,  9,  6,  8, 11,  2,  7,  0, 10],
            [ 4,  5,  6, 11,  8,  1, 12,  0,  9,  3,  7, 10],
            [ 5,  8,  2,  9,  7,  0, 12,  1, 10,  4,  6, 11],
            [ 2,  6, 12,  9,  0,  1,  7,  8,  5, 10, 11,  3]],

        [[ 9,  1,  3,  2, 12,  4,  7,  6, 11,  5,  8, 10],
            [ 6,  2,  7,  9,  8,  3,  0,  4, 10,  5, 11, 12],
            [11,  5,  7,  8,  3, 12, 10,  9,  1,  6,  0,  4],
            [ 5,  1,  2, 12,  4,  8, 11, 10,  9,  6,  0,  7],
            [10,  7,  6,  8,  1,  9, 11,  5,  0,  3, 12,  2]],

        [[ 1,  8,  7,  3,  4,  2,  6,  9, 11, 12,  5, 10],
            [ 3,  0,  9,  2,  6,  5,  4, 12, 11,  8, 10,  7],
            [12,  9,  8,  4,  0,  3,  1, 11, 10,  5,  7,  6],
            [12, 10,  7, 11,  2,  8,  5,  0,  4,  6,  9,  1],
            [ 3, 11,  6,  5, 12,  1,  2,  0, 10,  8,  7,  9]]])

@pytest.fixture()
def sample_dups():
    return np.array([7, 5, 1, 5, 3])