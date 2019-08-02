from autoleagueplay.generate_matches import get_playing_division_indices, load_all_bots, generate_round_robin_matches
from autoleagueplay.ladder import Ladder
from autoleagueplay.paths import WorkingDir


def list_matches(working_dir: WorkingDir, odd_week: bool):
    """
    Prints all the matches that will be run this week.
    """

    ladder = Ladder.read(working_dir.ladder)
    playing_division_indices = get_playing_division_indices(ladder, odd_week)

    print(f'Matches to play:')

    # The divisions play in reverse order, but we don't print them that way.
    for div_index in playing_division_indices:
        print(f'--- {Ladder.DIVISION_NAMES[div_index]} division ---')

        rr_bots = ladder.round_robin_participants(div_index)
        rr_matches = generate_round_robin_matches(rr_bots)

        for match_participants in rr_matches:
            print(f'{match_participants[0]} vs {match_participants[1]}')
