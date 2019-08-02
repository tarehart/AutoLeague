"""AutoLeague

Usage:
    autoleagueplay (odd | even) <ladder> [--replays=R] [--list]
    autoleagueplay (-h | --help)
    autoleagueplay --version

Options:
    --replays=R                  What to do with the replays of the match. Valid values are 'save', and 'calculated_gg'. [default: save]
    -l --list                    Instead of playing the matches, the list of matches is printed
    -h --help                    Show this screen.
    --version                    Show version.
"""

import sys
from pathlib import Path

from docopt import docopt

from autoleagueplay.list_matches import list_matches
from autoleagueplay.paths import WorkingDir
from autoleagueplay.replays import ReplayPreference
from autoleagueplay.run_matches import run_league_play
from autoleagueplay.version import __version__


def main():
    arguments = docopt(__doc__, version=__version__)

    ladder_path = Path(arguments['<ladder>'])
    if not ladder_path.exists():
        print(f'\'{ladder_path}\' does not exist.')
        sys.exit(1)

    working_dir = WorkingDir(ladder_path)

    replay_preference = ReplayPreference(arguments['--replays'])

    if arguments['odd'] or arguments['even']:
        if arguments['--list'] or arguments['-l']:
            list_matches(working_dir, arguments['odd'])
        else:
            run_league_play(working_dir, arguments['odd'], replay_preference)
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
