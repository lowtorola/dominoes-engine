from typing_extensions import Self


class InvalidMoveException(Exception):
    """
    Thrown when an invalid move is attempted during a game of Dominoes.
    """

    def __init__(self: Self, message: str):
        # TODO: add the ability to pass a "Move" and "Game State" into this constructor :)
        super().__init__(message)