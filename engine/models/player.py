from typing import Collection, Optional
from typing_extensions import Self
from engine.models.domino import Domino, DominoSet
from heapq import heapify, heappop, heappush


class Hand:
    """
    A Hand of Dominoes belonging to a Player in a game of Train Dominoes.
    """

    def __init__(self: Self, dominoes: Collection[Domino]) -> None:
        self.domino_list = list(dominoes)
        self.domino_set = DominoSet(dominoes)

        heapify(self.domino_list)

    def is_empty(self: Self) -> bool:
        """
        Returns whether this Hand contains no Dominoes.
        """
        return len(self.domino_list) == 0

    def peek_max(self: Self) -> Optional[Domino]:
        """
        Returns the Domino in this Hand with the largest point value.
        """
        if self.is_empty():
            return None
        else:
            return self.domino_list[0]
        
    def contains(self: Self, domino: Domino) -> bool:
        """
        Returns whether this Hand contains a given Domino.
        """
        return self.domino_set.contains(domino)


class Player:
    """
    A Player in a game of Train Dominoes with a unique name.
    Every Player has a unique hand of Dominoes.
    """

    def __init__(self: Self, hand, name):
        """
        Create a new Player with a DominoSet hand and a name.
        """
        self.hand = hand
        self.name = name
