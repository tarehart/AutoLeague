# -------------- STRUCTURE --------------
# league/
#     bots/
#         # Bot folders. E.g.:
#         skybot/..
#         botimus/..
#         ...
#     ladders/
#         # Contains files describing the ladder after each event
#         # Initial ladder is called 'ladder_0.json', next ladder generated after event 1 is called 'ladder_1.json' etc.
#         ladder_0.json
#         ladder_1.json
#         ladder_2.json
#     match_results/
#         # This directory contains directories with json files describing the match results
#         # The results in 'event_1/' resulted in 'ladder_1.json' based on 'ladder_0.json'
#         event_1/
#             # Following file describes the results of the match between bot1 and bot2
#             # in the quantum division round robin
#             quantum_bot1_vs_bot2_result.json
#             quantum_bot1_vs_bot3_result.json
#             ...
#         event_2/
#             overclocked_bot5_vs_bot6_result.json
#             overclocked_bot5_vs_bot7_result.json
#             ...
#
#
# A 'ladder_X.json' file contains a list of bot names. Their position is their rank on the ladder. E.g.:
# """[ Self-driving car, Botimus Prime, ReliefBot, ... ]"""
#
# A 'div_X_B1_vs_B2_result.json' file contains all relevant data from the match between B1 and B2 in division X. E.g.:
# """
# {
#     "blue": "ReliefBot",
#     "orange": "Botimus Prime",
#     "blue goals": 4,
#     "orange goals": 2,
#     "blue shots": 5,
#     "orange shots": 4,
#     "blue saves": 2,
#     "orange saves": 1,
#     "blue points": 630,
#     "orange points": 456,
# }
# """

"""
This module contains file system paths that are used by autoleague.
"""
import random
from pathlib import Path
from typing import Mapping

from rlbot.parsing.bot_config_bundle import BotConfigBundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs

from autoleague.ladder import Ladder


class WorkingDir:
    """
    An object to make it convenient and safe to access file system paths within the working directory.
    """

    def __init__(self, working_dir: Path):
        working_dir = working_dir.absolute()
        self._working_dir = working_dir
        self.ladders = working_dir / 'ladders'
        self.match_results = working_dir / 'match_results'
        self.bots = working_dir / 'bots'
        self._ensure_directory_structure()

    def _ensure_directory_structure(self):
        self._working_dir.mkdir(exist_ok=True)
        self.ladders.mkdir(exist_ok=True)
        self.match_results.mkdir(exist_ok=True)
        self.bots.mkdir(exist_ok=True)

    def get_ladder(self, index: int) -> Path:
        return self.ladders / f'ladder_{index}.json'

    def get_match_result_dir(self, event_number: int) -> Path:
        return self.match_results / f'event_{event_number}'

    def get_match_result(self, event_number: int, division_index: int, blue: str, orange: str) -> Path:
        match_name = f'{Ladder.DIVISION_NAMES[division_index]}_{blue}_vs_{orange}.json'
        return self.get_match_result_dir(event_number) / match_name

    def get_bots(self) -> Mapping[str, BotConfigBundle]:
        return {
            bot_config.name: bot_config
            for bot_config in scan_directory_for_bot_configs(self.bots)
        }


class PackageFiles:
    """
    An object to keep track of static paths that are part of this package
    """
    _package_dir = Path(__file__).absolute().parent
    default_match_config = _package_dir / 'default_match_config.cfg'

    _website_dir = _package_dir / 'website'
    additional_website_code = _website_dir / 'additional_website_code'
    additional_website_static = _website_dir / 'static'


def create_initial_ladder(working_dir: WorkingDir) -> Ladder:
    bots = [bot_config.name for bot_config in scan_directory_for_bot_configs(working_dir.bots)]
    random.shuffle(bots)
    ladder = Ladder(bots)
    ladder.write(working_dir.get_ladder(0))
    return ladder
