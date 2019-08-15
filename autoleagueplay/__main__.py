"""AutoLeague

Usage:
    autoleagueplay (odd | even | bubble) <ladder> [--replays=R] [--teamsize=T] [--list|--results]
    autoleagueplay fetch <week_num> <league_dir>
    autoleagueplay (-h | --help)
    autoleagueplay --version

Options:
    --replays=R                  What to do with the replays of the match. Valid values are 'save', and 'calculated_gg'. [default: calculated_gg]
    --teamsize=T                 How many players per team. [default: 1]
    --list                       Instead of playing the matches, the list of matches is printed.
    --results                    Like --list but also shows the result of matches that has been played.
    -h --help                    Show this screen.
    --version                    Show version.
"""

import sys
from pathlib import Path

from docopt import docopt

from autoleagueplay.bubble_sort import run_bubble_sort
from autoleagueplay.list_matches import list_matches
from autoleagueplay.paths import WorkingDir
from autoleagueplay.replays import ReplayPreference
from autoleagueplay.run_matches import run_league_play
from autoleagueplay.sheets import fetch_ladder_from_sheets
from autoleagueplay.version import __version__


def main():
    arguments = docopt(__doc__, version=__version__)

    if arguments['odd'] or arguments['even'] or arguments['bubble']:

        ladder_path = Path(arguments['<ladder>'])
        if not ladder_path.exists():
            print(f'\'{ladder_path}\' does not exist.')
            sys.exit(1)

        working_dir = WorkingDir(ladder_path)

        replay_preference = ReplayPreference(arguments['--replays'])
        team_size = int(arguments['--teamsize'])

        if arguments['--results']:
            list_matches(working_dir, arguments['odd'], True)
        elif arguments['--list']:
            list_matches(working_dir, arguments['odd'], False)
        elif arguments['bubble']:
            run_bubble_sort(working_dir, team_size, replay_preference)
        else:
            run_league_play(working_dir, arguments['odd'], replay_preference, team_size)

    elif arguments['fetch']:
        week_num = int(arguments['<week_num>'])
        if week_num < 0:
            print(f'Week number must be a positive integer.')
            sys.exit(1)

        league_dir = Path(arguments['<league_dir>'])
        if not league_dir.is_dir():
            league_dir = league_dir.parent
        league_dir.mkdir(exist_ok=True)
        ladder_path = league_dir / 'ladder.txt'

        ladder = fetch_ladder_from_sheets(week_num)
        ladder.write(ladder_path)

        print(f'Successfully fetched week {week_num} to \'{ladder_path}\'')
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
