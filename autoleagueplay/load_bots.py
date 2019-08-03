from typing import Dict, Mapping

from rlbot.parsing.bot_config_bundle import get_bot_config_bundle, BotConfigBundle

from autoleagueplay.paths import PackageFiles, WorkingDir

# Maps Psyonix bots to their skill value. Initialized in load_all_bots()
psyonix_bots: Dict[str, float] = dict()


def load_all_bots(working_dir: WorkingDir) -> Mapping[str, BotConfigBundle]:
    bots = dict(working_dir.get_bots())

    # Psyonix bots
    psyonix_allstar = get_bot_config_bundle(PackageFiles.psyonix_allstar)
    psyonix_pro = get_bot_config_bundle(PackageFiles.psyonix_pro)
    psyonix_rookie = get_bot_config_bundle(PackageFiles.psyonix_rookie)
    bots[psyonix_allstar.name] = psyonix_allstar
    bots[psyonix_pro.name] = psyonix_pro
    bots[psyonix_rookie.name] = psyonix_rookie
    # Skill values for later. This way the user can rename the Psyonix bots by changing the config files, but we still
    # have their correct skill
    psyonix_bots[psyonix_allstar.name] = 1.0
    psyonix_bots[psyonix_pro.name] = 0.5
    psyonix_bots[psyonix_rookie.name] = 0.0

    return bots
