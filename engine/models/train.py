from typing import Iterable
from typing_extensions import Self
from engine.constants import *
from engine.models.domino import Domino, DominoTree, TreeNode


class Train(DominoTree):
    """
    A Train of Dominoes in a game of Train Dominoes.
    The first Domino matches the Game's engine Domino,
    and each Domino matches the Domino before it in sequence.
    """

    def __init__(self: Self, player_name: str, engine: Domino) -> None:
        super().__init__()
        self.player_name = player_name
        self.engine = engine
        self.marked = False

    def __str__(self) -> str:
        return f"Train(player={self.player_name}, marked={self.marked})"

    def __repr__(self) -> str:
        return f"Train(player={self.player_name}, marked={self.marked}, ends={self.get_ends()})"

    def is_marked(self: Self) -> bool:
        """
        Returns whether this Train has a "marker", i.e. whether this
        Train can be played on by any Player.
        """
        return self.marked

    def set_marked(self: Self) -> None:
        """
        Add a marker to this Train so that any Player can add Dominoes to it.
        """
        self.marked = True
        return

    def set_unmarked(self: Self) -> None:
        """
        Remove this Train's marker, if it is present.
        """
        self.marked = False
        return

    def playable_ends(self: Self, dominoes: Iterable[Domino]) -> tuple[Domino]:
        """
        Returns all ends of the Train which match any of the provided Dominoes.
        If the Train is not begun, returns the engine (if it matches any of the Dominoes).
        If no Dominoes are provided, returns every end of the Train.
        """
        if self.is_empty():
            if len(dominoes) == 0:
                return (self.engine,)
            else:
                matches_engine = False
                for domino in dominoes:
                    if domino.matches(self.engine) or domino.matches_flipped(
                        self.engine
                    ):
                        matches_engine = True
                        break
                return (self.engine,) if matches_engine else tuple()
        else:
            return super().playable_ends(dominoes)
        
    def get_ends(self: Self) -> tuple[Domino]:
        """
        Get a tuple of the Dominoes at the ends of this Train.
        """
        if self.root is None:
            return (self.engine,)
        else:
            return tuple(self.ends.keys())

    def add_to_end(self: Self, end: Domino, domino: Domino) -> None:
        """
        Add a Domino to the given end of this Train. If the Domino does not match or
        the given end is not an end of this Train, raises an `InvalidMoveException`.
        """
        if self.is_empty() and end == self.engine:
            if domino.matches_flipped(end):
                domino.flip()
            if not domino.matches(end):
                raise Exception(f"Domino {domino} does not match desired end {end}.")
            domino_node = TreeNode(domino)
            self.root = domino_node
            self.ends = {domino: domino_node}
            self.ends_by_bottom = {domino.bottom: set([domino_node])}
        else:
            super().add_to_leaf(end, domino)
        return

    def add_to_leaf(self: Self, leaf: Domino, domino: Domino) -> None:
        """
        Not defined for Trains.
        """
        raise Exception("Cannot call add_to_leaf on Train.")


class CommunityTrain(Train):
    """
    The public community Train in a game of Train Dominoes. Any player
    who has started a Train can play on this Train in any turn.
    """

    def __init__(self: Self, engine: Domino) -> None:
        super().__init__(COMMUNITY_TRAIN, engine)
        self.marked = True

    def is_marked(self: Self) -> bool:
        return True

    def set_marked(self: Self) -> None:
        raise Exception("Cannot mark the community Train.")

    def set_unmarked(self: Self) -> None:
        raise Exception("Cannot un-mark the community Train.")
