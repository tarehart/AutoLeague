"""AutoLeague

Usage:
    autoleague (odd | even) <ladder> [--replays=R]
    autoleague (-h | --help)
    autoleague --version

Options:
    --replays=R                  What to do with the replays of the match. Valid values are 'save', and 'calculated_gg'. [default: save]
    -h --help                    Show this screen.
    --version                    Show version.
"""

import sys
from pathlib import Path

from docopt import docopt

from autoleague.paths import WorkingDir
from autoleague.replays import ReplayPreference
from autoleague.run_matches import run_league_play
from autoleague.version import __version__

ladder_arg = '<ladder>'


def main():
    arguments = docopt(__doc__, version=__version__)

    ladder_path = Path(arguments[ladder_arg])
    if not ladder_path.exists():
        print(f'\'{ladder_path}\' does not exist.')
        sys.exit(1)

    working_dir = WorkingDir(ladder_path)

    replay_preference = ReplayPreference(arguments['--replays'])

    if arguments['odd']:
        run_league_play(working_dir, True, replay_preference)
    elif arguments['even']:
        run_league_play(working_dir, False, replay_preference)
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
