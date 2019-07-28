import json
import math
import random
from pathlib import Path
from typing import List

from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs

from autoleague.paths import WorkingDir


class Ladder:
    DIVISION_NAMES = ['quantum', 'overclocked', 'processor', 'circuit', 'transistor', 'abacus', 'babbage',
                      'colossus', 'eniac', 'ferranti']

    def __init__(self, bots: List[str], division_size: int=4, overlap_size: int=1):
        self.bots = bots
        self.division_size = division_size
        self.overlap_size = overlap_size
        self.round_robin_size = division_size + overlap_size

    def division(self, division_index: int) -> List[str]:
        """
        Returns a list of bots in the division. Division at index 0 is Quantum, division at index 1 is Overclock, etc.
        """
        return self.bots[division_index * self.division_size:(1 + division_index) * self.division_size]

    def division_count(self) -> int:
        return math.ceil(len(self.bots) / self.division_size)

    def round_robin_participants(self, division_index: int) -> List[str]:
        """
        Returns a list of bots participating in the round robin based on division index. Division at index 0 is Quantum,
        division at index 1 is Overclock, etc.
        """
        return self.bots[division_index * self.division_size:(1 + division_index) * self.division_size + self.overlap_size]

    def write(self, path: Path):
        with open(path, 'w') as f:
            json.dump(self.bots, f, indent=4)

    @staticmethod
    def read(path: Path) -> 'Ladder':
        with open(path, 'r') as f:
            return Ladder(json.load(f))


def create_initial_ladder(working_dir: WorkingDir) -> Ladder:
    bots = [bot_config.name for bot_config in scan_directory_for_bot_configs(working_dir.bots)]
    random.shuffle(bots)
    ladder = Ladder(bots)
    ladder.write(working_dir.get_ladder(0))
    return ladder
