import json
import random
import shutil
import time
from enum import Enum
from pathlib import Path
from typing import Tuple, Mapping

from rlbot.matchconfig.conversions import as_match_config, read_match_config_from_file
from rlbot.matchconfig.match_config import MatchConfig, PlayerConfig, Team
from rlbot.parsing.bot_config_bundle import BotConfigBundle
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs
from rlbot.training.training import Fail
from rlbot.utils.logging_utils import get_logger
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.game_interface import GameInterface
from rlbottraining.exercise_runner import run_playlist
from rlbottraining.history.exercise_result import log_result, store_result, ExerciseResult
from rlbottraining.history.website.server import set_additional_website_code

from autoleague.generate_matches import generate_round_robin_matches
from autoleague.ladder import Ladder
from autoleague.match_exercise import MatchExercise, MatchGrader
from autoleague.match_result import CombinedScore, MatchResult
from autoleague.paths import WorkingDir, PackageFiles, create_initial_ladder
from autoleague.replays import ReplayPreference, ReplayMonitor

logger = get_logger('autoleague')


class RunOption(Enum):
    EVENT = 0
    ROUND_ROBIN = 1
    MATCH = 2


def run_matches(working_dir: WorkingDir, replay_preference: ReplayPreference):
    """
    Runs all matches as specified by working_dir/match_configs_todo
    """
    match_paths = list(working_dir.match_configs_todo.iterdir())
    if not len(match_paths):
        logger.warning(f'No matches found. Add some using `autoleague generate_matches`')
        return
    logger.info(f'Going to run {len(match_paths)} matches')
    match_configs = [ parse_match_config(p) for p in match_paths ]
    playlist = [
        MatchExercise(
            name='unnamed_match',
            match_config_file_name=match_path.name,
            match_config=match_config,
            grader=MatchGrader(
                replay_monitor=ReplayMonitor(replay_preference=replay_preference),
            )
        )
        for match_config, match_path in zip(match_configs, match_paths)
    ]

    set_additional_website_code(PackageFiles.additional_website_code, working_dir.history_dir)

    for result in run_playlist(playlist):
        store_result(result, working_dir.history_dir)
        match_config_file_name = result.exercise.match_config_file_name
        shutil.move(
            working_dir.match_configs_todo / match_config_file_name,
            working_dir.match_configs_done / match_config_file_name,
        )
        log_result(result, logger)


def parse_match_config(filepath: Path) -> MatchConfig:
    with open(filepath) as f:
        try:
            return json.load(f, object_hook=as_match_config)
        except Exception as e:
            print("Error while parsing:", filepath)
            raise e


def make_match_config(working_dir: WorkingDir, blue: BotConfigBundle, orange: BotConfigBundle) -> MatchConfig:
    match_config = read_match_config_from_file(PackageFiles.default_match_config)
    match_config.game_map = random.choice([
        'ChampionsField',
        'Farmstead',
        'StarbaseArc',
        'DFHStadium',
        'SaltyShores',
        'Wasteland',
    ])
    blue_path = str((Path(blue.config_directory) / blue.config_file_name).relative_to(working_dir.bots))
    orange_path = str((Path(orange.config_directory) / orange.config_file_name).relative_to(working_dir.bots))
    match_config.player_configs = [
        PlayerConfig.bot_config(working_dir.bots / blue_path, Team.BLUE),
        PlayerConfig.bot_config(working_dir.bots / orange_path, Team.ORANGE),
    ]
    return match_config


def find_newest_ladder(working_dir: WorkingDir) -> Tuple[Ladder, int]:
    """
    Returns the newest ladder stored in the working directory and its number.
    If no ladder is found a new initial ladder is generated (ladder 0).
    """
    ladder_path = working_dir.get_ladder(0)
    if not ladder_path.exists():
        # Initial ladder does not exist. Create initial ladder
        print('Creating initial ladder using random order.')
        ladder = create_initial_ladder(working_dir)
        return ladder, 0

    ladder_number = 0
    while True:
        next_ladder_path = working_dir.get_ladder(ladder_number + 1)
        if next_ladder_path.exists():
            ladder_path = next_ladder_path
            ladder_number += 1
        else:
            # ladder_path current points to our newest ladder. Load it
            ladder = Ladder.read(ladder_path)
            print(f'Starting from {ladder_path.name}')
            return ladder, ladder_number


def add_missing_bots(ladder: Ladder, bots: Mapping[str, BotConfigBundle]):
    """
    Any bot not on the ladder will be placed in the bottom of the ladder in a random order.
    """
    missing_bots = []
    for bot in bots.keys():
        if bot not in ladder.bots:
            missing_bots.append(bot)
    random.shuffle(missing_bots)
    ladder.bots.extend(missing_bots)
    if len(missing_bots) > 0:
        print(f'Bots added to bottom of ladder: {missing_bots}')


def progress_league_play(working_dir: WorkingDir, run_option: RunOption, replay_preference: ReplayPreference):
    """
    Progress League Play by playing the next event, round robin, or match as specified by the run_option.
    """

    # Load all bots
    bots = {bot_config.name: bot_config for bot_config in scan_directory_for_bot_configs(working_dir.bots)}
    if len(bots) < 2:
        # Not enough bots to play
        print(f'Not enough bots to run league play. Must have at least 2 (found {len(bots)})')
        return
    else:
        print(f'Loaded {len(bots)} bots')

    ladder, latest_event = find_newest_ladder(working_dir)
    current_event = latest_event + 1

    # FIXME: Bots should only be added to the ladder at the beginning of a new event, otherwise the script will notice some missing matches and things might get weird.
    add_missing_bots(ladder, bots)

    print(f'Starting event {current_event}')

    # We need the result of every match to create the next ladder. For each match in each round robin, if a result
    # exist already, it will be parsed, if it doesn't exist, it will be played.
    # When all results have been found, the new ladder can be completed and saved.
    new_ladder = Ladder(ladder.bots)
    event_results = []

    # Results from each round robin is stored here
    results_dir = working_dir.get_match_result_dir(current_event)
    results_dir.mkdir(exist_ok=True)

    # playing_division_indices contains even indices when event number is even and odd indices when event number is odd.
    # If there is only one division always play that division (division 0, quantum).
    playing_division_indices = range(ladder.division_count())[current_event % 2::2] if ladder.division_count() > 1 else [0]

    # The divisions play in reverse order, so quantum/overclocked division plays last
    for div_index in playing_division_indices[::-1]:
        print(f'Starting round robin for the {Ladder.DIVISION_NAMES[div_index]} division')

        rr_bots = ladder.round_robin_participants(div_index)
        rr_matches = generate_round_robin_matches(rr_bots)
        rr_results = []

        for match_participants in rr_matches:

            # Check if match has already been play, i.e. the result file already exist
            result_path = working_dir.get_match_result(current_event, div_index, match_participants[0], match_participants[1])
            if result_path.exists():
                # Found existing result
                try:
                    print(f'Found existing result {result_path.name}')
                    result = MatchResult.read(result_path)

                    rr_results.append(result)

                except Exception as e:
                    print(f'Error loading result {result_path.name}. Fix/delete the result and run script again.')
                    raise e

            else:
                # Play the match
                print(f'Starting match: {match_participants[0]} vs {match_participants[1]}. Waiting for match to finish...')
                match_config = make_match_config(working_dir, bots[match_participants[0]], bots[match_participants[1]])
                match = MatchExercise(
                    name=f'{match_participants[0]} vs {match_participants[1]}',
                    match_config=match_config,
                    grader=MatchGrader(
                        replay_monitor=ReplayMonitor(replay_preference=replay_preference),
                    )
                )

                # For loop, but should only run exactly once
                for exercise_result in run_playlist([match]):

                    # Warn users if no replay was found
                    if isinstance(exercise_result.grade, Fail) and exercise_result.exercise.grader.replay_monitor.replay_id == None:
                        print(f'WARNING: No replay was found for the match \'{match_participants[0]} vs {match_participants[1]}\'. Is Bakkesmod injected and \'Automatically save all replays\' enabled?')

                    # Save result in file
                    result = exercise_result.exercise.grader.match_result
                    result.write(result_path)
                    print(f'Match finished {result.blue_goals}-{result.orange_goals}. Saved result as {result_path}')

                    rr_results.append(result)

                    # Let the winner celebrate and the scoreboard time enough to appear for a few seconds.
                    # This sleep not required unnecessary.
                    time.sleep(8)

        print(f'{Ladder.DIVISION_NAMES[div_index]} division done')
        event_results.append(rr_results)

        # Find bots' overall score for the round robin
        overall_scores = [CombinedScore.calc_score(bot, rr_results) for bot in rr_bots]
        sorted_overall_scores = sorted(overall_scores)[::-1]
        print(f'Bots\' overall performance in {Ladder.DIVISION_NAMES[div_index]} division:')
        for score in sorted_overall_scores:
            print(f'> {score.bot}: goal_diff={score.goal_diff}, goals={score.goals}, shots={score.shots}, saves={score.saves}, points={score.points}')

        # Rearrange bots on ladder
        first_bot_index = new_ladder.division_size * div_index
        bots_to_rearrange = len(rr_bots)
        for i in range(bots_to_rearrange):
            new_ladder.bots[first_bot_index + i] = sorted_overall_scores[i].bot

    print(f'Event {current_event} over')

    # Save new ladder
    new_ladder_path = working_dir.get_ladder(current_event)
    Ladder.write(new_ladder, new_ladder_path)
    print(f'Saved new ladder as {new_ladder_path.name}')

    return new_ladder
