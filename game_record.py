from typing import Union


class GameRecord:
    ROW_DATA_EXPECTED_LEN = 4

    @classmethod
    def from_row(cls, row_data):
        if len(row_data) != cls.ROW_DATA_EXPECTED_LEN:
            raise ValueError(f"Can't create GameRecord from row_data: {row_data} (length = 4 is required)")
        return cls(
            first_player=row_data[0],
            second_player=row_data[1],
            first_player_score=float(row_data[2]),
            second_player_score=float(row_data[3]),
        )

    def __init__(
            self,
            first_player: str,
            second_player: str,
            first_player_score: Union[float, int],
            second_player_score: Union[float, int],
    ):
        self.first_player = first_player
        self.second_player = second_player
        self.first_player_score = first_player_score
        self.second_player_score = second_player_score
