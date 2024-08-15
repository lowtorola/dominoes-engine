from typing import Collection, Any, Optional
from typing_extensions import Self
from engine.models.exceptions import InvalidMoveException


class Domino:
    """
    Dominos are oriented vertically, such that to "match"
    the bottom of the upper Domino must equal the top of the lower Domino.
    Each Domino can occur in a game at most once.
    """

    # TODO: implement doubles! they are played perpendicularly!

    def __init__(self: Self, top: int, bottom: int) -> None:
        self.top = top
        self.bottom = bottom
        return

    def __eq__(self: Self, other: Any) -> bool:
        return (
            isinstance(other, Domino)
            and (self.top == other.top and self.bottom == other.bottom)
            or (self.top == other.bottom and self.bottom == other.top)
        )
    
    def __lt__(self: Self, other: Any) -> bool:
        if not isinstance(other, Domino):
            raise Exception(f"Cannot compare Domino {self} to {other.__class__()} {other}.")
        else:
            return self.value() > other.value()
    
    def __le__(self: Self, other: Any) -> bool:
        if not isinstance(other, Domino):
            raise Exception(f"Cannot compare Domino {self} to {other.__class__()} {other}.")
        else:
            return self.value() >= other.value()

    def __gt__(self: Self, other: Any) -> bool:
        if not isinstance(other, Domino):
            raise Exception(f"Cannot compare Domino {self} to {other.__class__()} {other}.")
        else:
            return self.value() < other.value()

    def __ge__(self: Self, other: Any) -> bool:
        if not isinstance(other, Domino):
            raise Exception(f"Cannot compare Domino {self} to {other.__class__()} {other}.")
        else:
            return self.value() <= other.value()
    
    def __hash__(self: Self):
        return tuple(sorted([self.top, self.bottom]))
    
    def __str__(self: Self) -> str:
        return f"Domino(top={self.top}, bottom={self.bottom})"
    
    def __repr__(self: Self) -> str:
        return f"Domino(top={self.top}, bottom={self.bottom})"

    def value(self: Self) -> int:
        """
        Returns the point value of this Domino.
        """
        if self.top == 0 and self.bottom == 0:
            return 50
        else:
            return self.top + self.bottom

    def flip(self: Self) -> None:
        """
        Flips this Domino 180 degrees vertically on the game board.
        """
        self.top, self.bottom = self.bottom, self.top
        return

    def matches(self: Self, above: Any) -> bool:
        """
        Returns true if the above Domino's bottom matches with this Domino's top.
        """
        return isinstance(above, Domino) and self.top == above.bottom

    def matches_flipped(self: Self, above: Any) -> bool:
        """
        Returns true if the above Domino's bottom matches with this Domino's bottom.
        """
        return isinstance(above, Domino) and self.bottom == above.top


class DominoSet:
    """
    An unordered Set of unique Dominoes.
    """

    def __init__(self: Self, dominoes: Collection[Domino]) -> None:
        self.dominoes = set(dominoes)
        return
    
    def contains(self: Self, domino: Domino) -> bool:
        """
        Returns whether this Set contains a given Domino.
        """
        return domino in self.dominoes

    def draw_random(self: Self) -> Domino:
        """
        Draws, removes, and returns a random Domino from this Set.
        """
        return self.dominoes.pop()


class DominoSequence:
    """
    An ordered Sequence of Dominoes. Every Domino matches
    the Dominoes above and below it if they exist.
    """

    # TODO: support doubles! they should always be played sideways!

    def __init__(self: Self, dominoes: Collection[Domino]) -> None:
        self.dominoes = list(dominoes)
        return

    def get_front(self: Self) -> Optional[Domino]:
        """
        Returns the Domino at the beginning of this Sequence, if one exists.
        """
        return self.dominoes[0] if len(self.dominoes) > 0 else None

    def get_end(self: Self) -> Optional[Domino]:
        """
        Returns the Domino at the end of this Sequence, if one exists.
        """
        return self.dominoes[-1] if len(self.dominoes) > 0 else None

    def fits_at_end(self: Self, domino: Domino) -> bool:
        """
        Returns true if the Domino matches at the end of this Sequence in any orientation.
        If the Domino fits once it is flipped, it is flipped.
        If this Sequence is empty, any Domino fits at its end.
        """
        end = self.get_end()

        if end is None:
            return True
        elif domino.matches_flipped(end):
            domino.flip()

        return domino.matches(end)
    
    def add_to_end(self: Self, domino: Domino) -> None:
        """
        Add a domino to the end of this Sequence, if it fits.
        If it does not fit, raises `InvalidMoveException`
        """
        if not self.fits_at_end(domino):
            raise InvalidMoveException(f"Cannot add {domino} to Sequence ending with {self.get_end()}.")
        else:
            self.dominoes.append(domino)
