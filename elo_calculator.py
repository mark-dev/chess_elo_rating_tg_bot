import logging

from typing import List, Union, Any
from game_record import GameRecord
from player_info import PlayerInfo

from elopy.elo import Elo

logger = logging.getLogger(__name__)


class EloCalculator:
    _players: dict[str, PlayerInfo]

    DEFAULT_RATING = 1500

    def __init__(self, known_players: List[PlayerInfo]):
        self._players = {p.name: p for p in known_players}

    def evaluate_game_records(
            self,
            games: List[GameRecord]
    ) -> List[PlayerInfo]:
        for g in games:
            first_player = self.get_player_by_name(g.first_player)
            second_player = self.get_player_by_name(g.second_player)
            score_diff = g.first_player_score - g.second_player_score

            elo_team_a = Elo(start_elo=first_player.rating, k=100, hca=0)
            elo_team_b = Elo(start_elo=second_player.rating, k=100, hca=0)
            elo_team_a.play_game(elo_team_b, point_difference=score_diff)

            # Update game count
            first_player.game_count += 1
            second_player.game_count += 1
            # Calc ELO diff
            first_player_rating_diff = int(elo_team_a.elo - first_player.rating)
            second_player_rating_diff = int(elo_team_b.elo - second_player.rating)

            # Save new ELO
            first_player.rating += first_player_rating_diff
            second_player.rating += second_player_rating_diff

            logger.info(
                '%s (%s) <--> %s (%s) ',
                first_player.name,
                first_player_rating_diff if first_player_rating_diff <= 0 else f'+{first_player_rating_diff}',
                second_player.name,
                second_player_rating_diff if second_player_rating_diff <= 0 else f'+{second_player_rating_diff}',
            )

        return list(self._players.values())

    def get_player_by_name(self, name):
        name = name.strip()
        player = self._players.get(name)
        if player:
            return player

        p = PlayerInfo(name, self.DEFAULT_RATING, 0)
        self._players[name] = p

        return p
