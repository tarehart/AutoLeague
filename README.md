# AutoLeague for League Play
[DomNomNom's Autoleague](https://github.com/DomNomNom/AutoLeague) modified to play [RLBot](http://rlbot.org/)'s Official League Play.

# How to use:

You must use [Bakkesmod](https://bakkesmod.com/) and have 'Automatically save all replays' enabled.

To run most commands, you'll need to specify a `--working_dir` flag or alternatively, you can set a `AUTOLEAGUE_WORKING_DIR` environment variable to save yourself future typing.

Usage:
```
autoleague next_event          | Finish the next event (week)
autoleague next_round_robin    | Finish the next round robin
autoleague next_match          | Finish the next match
autoleague (-h | --help)       | Show commands and options
autoleague --version           | Show version
```

Options:
```
--working_dir=<working_dir>  | Where to store inputs and outputs of the league.
--replays=R                  | What to do with the replays of the match. Valid values are 'save', and 'calculated_gg'. [default: calculated_gg]
```

Note: The project is work-in-progress and might not fully adhere to the above (yet)