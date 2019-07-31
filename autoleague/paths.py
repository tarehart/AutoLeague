# -------------- STRUCTURE --------------
# <ladder>.txt   # Given through arguments. Contains current ladder. Bot names separated by newlines.
# <ladder>_new.txt   # The ladder generated. Contains resulting ladder. Bot names separated by newlines.
# bots/
#     skybot/..
#     botimus/..
#     ...
# <ladder>_results/
#     # This directory contains the match results. One json file for each match with all the info
#     quantum_bot1_vs_bot2_result.json
#     quantum_bot1_vs_bot3_result.json
#     ...
#

"""
This module contains file system paths that are used by autoleague.
"""
from pathlib import Path
from typing import Mapping

from rlbot.parsing.bot_config_bundle import BotConfigBundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs

from autoleague.ladder import Ladder


class WorkingDir:
    """
    An object to make it convenient and safe to access file system paths within the working directory.
    """

    def __init__(self, ladder_path: Path):
        working_dir = ladder_path.parent.absolute()
        self._working_dir = working_dir
        self.ladder = ladder_path
        self.new_ladder = self._working_dir / f'{ladder_path.stem}_new.txt'
        self.match_results = working_dir / f'{ladder_path.stem}_results'
        self.bots = working_dir / 'bots'
        self._ensure_directory_structure()

    def _ensure_directory_structure(self):
        self.match_results.mkdir(exist_ok=True)
        self.bots.mkdir(exist_ok=True)

    def get_match_result(self, division_index: int, blue: str, orange: str) -> Path:
        match_name = f'{Ladder.DIVISION_NAMES[division_index]}_{blue}_vs_{orange}.json'
        return self.match_results / match_name

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
