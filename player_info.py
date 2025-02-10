class PlayerInfo:

    def __init__(self, name: str, rating: int, game_count: int):
        self.name = name
        self.rating = rating
        self.game_count = game_count

    @classmethod
    def get_row_data_title(cls):
        return [
            'Имя',
            'Рейтинг',
            'Кол-во игр'
        ]

    @classmethod
    def from_excel_row_data(cls, row_data):
        player_name = row_data[0]
        if not player_name:
            return None

        return cls(
            name=row_data[0].strip(),
            rating=int(row_data[1]),
            game_count=int(row_data[2] or 0),
        )

    def to_excel_row_data(self):
        return [
            self.name,
            self.rating,
            self.game_count
        ]
