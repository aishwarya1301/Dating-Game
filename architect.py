from dating import Person
import sys
import numpy as np


ATTRIBUTES = 5
port = int(sys.argv[1])


def sample_candidate(weights):
    """Sample a candidate such that their score is not 1. Otherwise we would
    have solved the problem for the matchmaker.
    """

    n = len(weights)
    candidate = np.random.randint(0, 2, size=n)
    while weights*candidate == 1:
        candidate = np.random.randint(0, 2, size=n)

    return candidate

best_score = -np.inf
person = Person(ATTRIBUTES, port)

for i in range(20):
    candidate = sample_candidate(
