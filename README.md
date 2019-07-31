# AutoLeague for League Play
[DomNomNom's Autoleague](https://github.com/DomNomNom/AutoLeague) modified to play [RLBot](http://rlbot.org/)'s Official League Play.

# How to use:

Recommended: Use [Bakkesmod](https://bakkesmod.com/) and have 'Automatically save all replays' enabled.

Usage:
```
autoleague (odd | even) <path/to/current/ladder.txt>  | Plays an odd or even week from the given ladder
autoleague (-h | --help)                              | Show commands and options
autoleague --version                                  | Show version
```

Options:
```
--replays=R          What to do with the replays of the match. Valid values are 'save', and 'calculated_gg'. [default: save]
-h --help            Show this screen.
--version            Show version.
```


The ladder is described by a text file, e.g. `ladder.txt`.
This should contain the bot names separated by newlines (it can be copy-pasted directly from the sheet).
A `bots` directory with all the bots and their files must be located next to the ladder file.

When running the script you point it to the ladder file and give it either `odd` or `even` as argument to set what type of week it should play:
- Odd: Overclocked, Circuit, Transitor, ect plays.
- Even: Quantum, Processor, Abacus, etc plays.

Results are stored in a matches directory next to the ladder file. Each match will get a json file with all the relevant data, and they are named something like `quantum_ReliefBot_vs_Atlas_result.json`.
When all results are found, a new ladder `ladder_new.txt` is created next to the original ladder file.

#### Other:

Change `autoleague/default_match_config.cfg` for other game modes and mutators.