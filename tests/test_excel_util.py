import excel_util


def test_load_player_info():
    players = excel_util.read_players_from_excel('files/player_info.xlsx')
    assert players
    assert len(players) == 3


def test_load_game_records():
    games = excel_util.read_game_records_from_excel('files/game_records.xlsx')
    assert games
    assert len(games) == 2

    g = games[0]
    assert g.first_player == 'Марк'
    assert g.second_player == 'Александр'
    assert g.first_player_score == 1
    assert g.second_player_score == 0
