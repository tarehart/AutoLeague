from os.path import relpath

from git import Repo
from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs

from autoleagueplay.ladder import Ladder
from autoleagueplay.match_configurations import make_match_config
from autoleagueplay.match_result import MatchResult
from autoleagueplay.paths import WorkingDir
from autoleagueplay.replays import ReplayPreference
from autoleagueplay.run_matches import run_match
from autoleagueplay.versioned_bot import VersionedBot


class BubbleSorter:

    def __init__(self, ladder: Ladder, working_dir: WorkingDir, team_size: int,
                 replay_preference: ReplayPreference):
        self.ladder = ladder
        self.bots = ladder.bots
        self.working_dir = working_dir
        self.team_size = team_size
        self.replay_preference = replay_preference
        self.bundle_map = {}
        self.versioned_bots_by_name = {}
        self.num_already_played_during_iteration = 0

    def pull_bots(self):
        git_root = self.working_dir._working_dir
        repo = Repo(git_root)
        repo.remote().pull()

        bot_folders = [p for p in self.working_dir.bots.iterdir() if p.is_dir()]

        versioned_bots = set()

        for folder in bot_folders:
            relative_path = relpath(folder, git_root)
            latest_commit = list(repo.iter_commits(paths=relative_path, max_count=1))[0]
            for bot_config in scan_directory_for_bot_configs(folder):
                versioned_bot = VersionedBot(bot_config, latest_commit)
                print(versioned_bot)
                versioned_bots.add(versioned_bot)

        self.bundle_map = {
            vb.get_unversioned_key(): vb.bot_config
            for vb in versioned_bots
        }
        self.versioned_bots_by_name = {
            vb.get_unversioned_key(): vb
            for vb in versioned_bots
        }

        bots_not_in_ladder = set([vb.get_unversioned_key() for vb in versioned_bots]).difference(set(self.bots))
        self.bots.extend(bots_not_in_ladder)
        self.ladder.write(self.working_dir.ladder)

    def begin(self):
        self.pull_bots()
        num_bots = len(self.bots)
        if num_bots < 2:
            raise Exception(f'Need at least 2 bots to run a bubble sort! Found {num_bots}')
        self.num_already_played_during_iteration = 0
        self.advance(num_bots - 2)

    def get_past_result(self, bot_1, bot_2) -> MatchResult:
        path = self.get_result_path(bot_1, bot_2)
        if path.exists():
            try:
                print(f'Found existing result {path.name}')
                return MatchResult.read(path)
            except Exception as e:
                print(f'Error loading result {path.name}. Fix/delete the result and run script again.')
                raise e
        return None

    def get_result_path(self, bot_1, bot_2):
        versioned_bot_1 = self.versioned_bots_by_name[bot_1]
        versioned_bot_2 = self.versioned_bots_by_name[bot_2]
        return self.working_dir.get_version_specific_match_result(versioned_bot_1, versioned_bot_2)

    def _on_match_complete(self, result):

        winner = result.winner.lower()
        loser = result.loser.lower()

        winner_index = self.bots.index(winner)
        loser_index = self.bots.index(loser)

        if winner_index > loser_index:
            # Need to swap the indices!
            self.bots[loser_index] = winner
            self.bots[winner_index] = loser

        self.advance(min(winner_index, loser_index))

    def advance(self, upper_index):

        num_bots = len(self.bots)

        if upper_index == 0:
            # We've reached the top, time to jump back to the bottom (or decide we're done)
            if self.num_already_played_during_iteration == num_bots - 1:
                return  # bubble sort is over!
            else:
                next_below = self.bots[num_bots - 1]
                next_above = self.bots[num_bots - 2]
                self.num_already_played_during_iteration = 0
        else:
            next_above = self.bots[upper_index - 1]
            next_below = self.bots[upper_index]

        past_result = self.get_past_result(next_above, next_below)

        if past_result is not None:
            self.num_already_played_during_iteration += 1
            self._on_match_complete(past_result)
        else:
            match_config = make_match_config(self.bundle_map[next_below], self.bundle_map[next_above], self.team_size)
            match_result = run_match(next_below, next_above, match_config, self.replay_preference)
            match_result.write(self.get_result_path(next_below, next_above))
            self.ladder.write(self.working_dir.ladder)
            self._on_match_complete(match_result)


def run_bubble_sort(working_dir: WorkingDir, team_size: int, replay_preference: ReplayPreference):

    # Ladder is a list of name.lower()
    ladder = Ladder.read(working_dir.ladder)

    sorter = BubbleSorter(ladder, working_dir, team_size, replay_preference)
    sorter.begin()
