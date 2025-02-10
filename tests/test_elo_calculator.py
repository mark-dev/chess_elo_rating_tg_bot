import logging
from typing import List
from venv import logger

from elo_calculator import EloCalculator
from game_record import GameRecord
from player_info import PlayerInfo

import excel_util

logger = logging.getLogger(__name__)


def test_elo_calculator():
    calculator = EloCalculator(known_players=[])
    game1 = GameRecord(
        first_player='Марк',
        second_player='Александр',
        first_player_score=1,
        second_player_score=0
    )

    game2 = GameRecord(
        first_player='Регина',
        second_player='Александр',
        first_player_score=0.5,
        second_player_score=0.5
    )

    game3 = GameRecord(
        first_player='Регина',
        second_player='Марк',
        first_player_score=1,
        second_player_score=0
    )

    games = [game1, game2, game3]

    new_players: List[PlayerInfo] = calculator.evaluate_game_records(games)

    assert len(new_players) == 3
    new_players.sort(key=lambda x: -x.rating)

    top_rated = new_players[0]
    assert top_rated.name == 'Регина'
    assert top_rated.game_count == 2


def test_elo_calculator_real_data():
    calculator = EloCalculator(known_players=[])
    game_records = excel_util.read_game_records_from_excel('files/2025_02_07.xlsx')

    new_players: List[PlayerInfo] = calculator.evaluate_game_records(game_records)

    new_players.sort(key=lambda x: -x.rating)

    for p in new_players:
        logger.info('%s => %s', p.name, p.rating)

    assert new_players
