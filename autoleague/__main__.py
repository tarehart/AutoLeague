"""AutoLeague

Usage:
    autoleague next_event          [--working_dir=<working_dir>][--replays=R] TODO
    autoleague next_round_robin    [--working_dir=<working_dir>] [--replays=R] TODO
    autoleague next_match          [--working_dir=<working_dir>] [--replays=R] TODO
    autoleague history_dev_server  [--working_dir=<working_dir>] [--host=<host>] [--port=<port>] TODO
    autoleague (-h | --help)
    autoleague --version

Options:
    --working_dir=<working_dir>  Where to store inputs and outputs of the league.
    --replays=R                  What to do with the replays of the match. Valid values are 'save', and 'calculated_gg'. [default: calculated_gg]
    --host=<host>            [default: localhost].
    --port=<port>            [default: 8878]
    -h --help                    Show this screen.
    --version                    Show version.
"""

from pathlib import Path
import os
import sys
import subprocess

from docopt import docopt

from autoleague.paths import WorkingDir
from autoleague.run_matches import run_matches
from autoleague.version import __version__
from autoleague.replays import ReplayPreference


working_dir_env_var = 'AUTOLEAGUE_WORKING_DIR'
working_dir_flag = '--working_dir'


def main():
    arguments = docopt(__doc__, version=__version__)

    working_dir = arguments[working_dir_flag]
    if working_dir is None:
        working_dir = os.environ.get(working_dir_env_var, None)
    if working_dir is None:
        print('The working directory must be specified. You can specify it in one of these ways:')
        print(f'  Use the {working_dir_flag} flag')
        print(f'  Use the {working_dir_env_var} environment variable')
        sys.exit(1)
    working_dir = WorkingDir(Path(working_dir))

    if arguments['next_event']:
        replay_preference = ReplayPreference(arguments['--replays'])
        run_next_event(working_dir, replay_preference)
    elif arguments['next_round_robin']:
        replay_preference = ReplayPreference(arguments['--replays'])
        run_next_round_robin(working_dir, replay_preference)
    elif arguments['next_round_robin']:
        replay_preference = ReplayPreference(arguments['--replays'])
        run_next_match(working_dir, replay_preference)
    elif arguments['history_dev_server']:
        subprocess.run(
            f'rlbottraining history_dev_server {working_dir.history_dir} --host="{arguments["--host"]}" --port={int(arguments["--port"])}',
            shell=True,
        )
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
