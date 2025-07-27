from typing_extensions import Self


class InvalidMoveException(Exception):
    """
    Thrown when a Player attempts an invalid move during a game of Dominoes.
    Contains a hashable representation of the Game state before the invalid move.
    """

    def __init__(self: Self, message: str, prev_state: str) -> None:
        super().__init__(message)
        self.prev_state = prev_state