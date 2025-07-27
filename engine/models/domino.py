from typing import Collection, Any, Iterable, Optional
from typing_extensions import Self


class Domino:
    """
    Dominos are oriented vertically, such that to "match"
    the bottom of the upper Domino must equal the top of the lower Domino.
    Each Domino can occur in a game at most once.
    """

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
            raise Exception(
                f"Cannot compare Domino {self} to {other.__class__()} {other}."
            )
        else:
            return self.value() > other.value()

    def __le__(self: Self, other: Any) -> bool:
        if not isinstance(other, Domino):
            raise Exception(
                f"Cannot compare Domino {self} to {other.__class__()} {other}."
            )
        else:
            return self.value() >= other.value()

    def __gt__(self: Self, other: Any) -> bool:
        if not isinstance(other, Domino):
            raise Exception(
                f"Cannot compare Domino {self} to {other.__class__()} {other}."
            )
        else:
            return self.value() < other.value()

    def __ge__(self: Self, other: Any) -> bool:
        if not isinstance(other, Domino):
            raise Exception(
                f"Cannot compare Domino {self} to {other.__class__()} {other}."
            )
        else:
            return self.value() <= other.value()

    def __hash__(self: Self) -> int:
        return hash(tuple(sorted([self.top, self.bottom])))

    def __str__(self: Self) -> str:
        return f"Domino({self.top}, {self.bottom})"

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
        return isinstance(above, Domino) and self.bottom == above.bottom

    def is_double(self: Self) -> bool:
        """
        Returns true if this Domino's top and bottom are equal.
        """
        return self.top == self.bottom


class DominoSet:
    """
    An unordered Set of unique Dominoes.
    """

    def __init__(self: Self, dominoes: Collection[Domino]) -> None:
        self.dominoes = set(dominoes)
        return

    def __sizeof__(self: Self) -> int:
        return len(self.dominoes)

    def __len__(self: Self) -> int:
        return len(self.dominoes)

    def contains(self: Self, domino: Domino) -> bool:
        """
        Returns whether this Set contains a given Domino.
        """
        return domino in self.dominoes

    def add(self, domino: Domino) -> None:
        """
        Add the given Domino to this Set.
        """
        self.dominoes.add(domino)
        return

    def draw_random(self: Self) -> Domino:
        """
        Draws, removes, and returns a random Domino from this Set.
        """
        return self.dominoes.pop()

    def draw(self: Self, domino: Domino) -> Domino:
        """
        Draws, removes, and returns the given domino from this Set.
        If the domino is not in this Set, raises an Exception
        """
        if not self.contains(domino):
            raise Exception(f"Requested DominoSet does not contain {domino}.")
        else:
            self.dominoes.discard(domino)
            return domino

    def all_matching(self: Self, to_match: Domino) -> tuple[Domino]:
        """
        Returns all Dominoes in this Set which match the given Domino.
        All returned Dominoes will be flipped so that their tops match the
        given Domino's bottom.
        """
        output: list[Domino] = []
        for domino in self.dominoes:
            if domino.matches_flipped(to_match):
                domino.flip()
            if domino.matches(to_match):
                output.append(domino)
        return tuple(output)


class TreeNode:
    """
    A node in the Domino tree. Doubles can have at most two children,
    and all other Dominoes can have at most one child.
    """

    def __init__(self: Self, domino: Domino, *children: Domino) -> None:
        self.domino = domino

        if len(children) > 2:
            raise Exception(f"Cannot chain more than two Dominoes.")
        elif not domino.is_double() and len(children) > 1:
            raise Exception(f"Cannot fork for non-double Domino {domino}.")
        else:
            self.children = children
        return

    def get_children(self: Self) -> tuple[Domino]:
        """
        Returns all of the children of this TreeNode as a tuple.
        """
        return self.children

    def is_complete(self: Self) -> bool:
        """
        Returns whether this node has a maximal number of children.
        """
        return (self.domino.is_double() and len(self.children) >= 2) or (
            not self.domino.is_double() and len(self.children) >= 1
        )

    def add_child(self: Self, child: Domino) -> None:
        """
        Adds the given Domino as a child of this node if this node is not
        complete. If the node is complete, raises an `Exception`.
        """
        if self.is_complete():
            raise Exception("Cannot add child to complete tree node.")
        else:
            self.children = (*self.children, child)
        return


class DominoTree:
    """
    A directed tree with Domino nodes. Doubles have up to two children,
    and all other Dominoes have up to one child. Every Domino matches its
    parent if it has one.
    """

    def __init__(self: Self) -> None:
        # Map from end.bottom to all ends with that bottom
        self.ends_by_bottom: dict[int, set[TreeNode]] = dict()

        # Set of all ends
        self.ends: dict[Domino, TreeNode] = dict()

        # The root of the tree (the Domino after the engine)
        self.root: Optional[TreeNode] = None

    def is_empty(self: Self) -> bool:
        """
        Returns whether this Tree contains no Dominoes.
        """
        return self.root is None

    def playable_ends(
        self: Self, dominoes: Iterable[Domino]
    ) -> Optional[tuple[Domino]]:
        """
        Returns all leaves of the Tree which match any of the provided Dominoes.
        If the Tree is empty, returns None. If no Dominoes are provided, returns
        every leaf in the Tree.
        """
        if self.root is None:
            return
        elif len(dominoes) == 0:
            return tuple([end for end in self.ends])
        else:
            # We only need to consider ends which match either side of any of the Dominoes
            consider_ends: set[int] = set()
            for domino in dominoes:
                consider_ends.add(domino.top)
                consider_ends.add(domino.bottom)
            # Now return any ends which match
            output: set[Domino] = set()
            for end_val, end_nodes in self.ends_by_bottom.items():
                if end_val in consider_ends:
                    output.update(set([end_node.domino for end_node in end_nodes]))
            return tuple(output)

    def add_to_leaf(self: Self, leaf: Domino, domino: Domino) -> None:
        """
        Add a Domino to the given leaf of this Tree. If the Domino does not match or
        the given end is not an end of this Tree, raises an `InvalidMoveException`.
        """
        # Ensure that the Domino can be added to the valid leaf
        if leaf not in self.ends:
            raise Exception(f"Provided leaf {leaf} is not a valid leaf in the tree.")
        if domino.matches_flipped(leaf):
            domino.flip()
        if not domino.matches(leaf):
            raise Exception(f"Domino {domino} does not match desired parent {leaf}.")

        leaf_node = self.ends[leaf]

        # Add this Domino as a child of the leaf
        leaf_node.add_child(domino)

        # Add this Domino to the ends
        domino_node = TreeNode(domino)
        self.ends[domino] = domino_node
        if domino.bottom not in self.ends_by_bottom:
            self.ends_by_bottom[domino.bottom] = set()
        self.ends_by_bottom[domino.bottom].add(domino_node)

        # If the leaf is now complete, remove it from the ends
        if leaf_node.is_complete():
            del self.ends[leaf]
            self.ends_by_bottom[leaf.bottom].remove(leaf_node)
            if len(self.ends_by_bottom[leaf.bottom]) == 0:
                del self.ends_by_bottom[leaf.bottom]
        return
