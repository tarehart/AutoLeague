import random
from typing import List, Tuple


def generate_round_robin_matches(bots: List[str]) -> List[Tuple[str, str]]:
    """
    Returns a list of pairs of bots that should play against each other for a round robin.
    """
    # Create all possible pairs of bots with bots from the given list
    matches = []
    count = len(bots)
    for i in range(count):
        for j in range(i + 1, count):
            matches.append((bots[i], bots[j]))

    random.shuffle(matches)
    return matches

