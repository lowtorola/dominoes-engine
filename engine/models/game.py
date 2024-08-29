from typing import Any, Collection, Iterable, Iterator, Optional
from engine.constants import *
from engine.models.domino import Domino, DominoTree, DominoSet, TreeNode
from engine.models.exceptions import InvalidMoveException
from typing_extensions import Self
from random import choice


class Player(DominoSet):
    """
    A Player in a game of Train Dominoes with a unique name.
    Every Player has a hand of unique Dominoes.
    """

    def __init__(self: Self, name: str):
        """
        Create a new Player with a unique name.
        """
        self.name = name
        super().__init__([])

    def __hash__(self: Self) -> int:
        return hash(self.name)

    def __eq__(self: Self, other: Any) -> bool:
        return isinstance(other, Player) and self.name == other.name

    def __str__(self: Self) -> str:
        return f"Player({self.name})"

    def __repr__(self: Self) -> str:
        return f"Player(name={self.name})"

    def make_move(self: Self, playable_trains: list) -> None:
        """
        Plays a move for this Player onto one of the Trains.
        If the Player cannot move, they will do nothing.
        """
        if len(playable_trains) == 0:
            raise Exception(
                "Expected Players to always at least be able to play on their own Train."
            )
        # Greedy: play the first Domino we are able to onto the first Train
        for train in playable_trains:
            ends = train.playable_ends(self.dominoes)
            if ends is None or len(ends) == 0:
                continue
            for end in ends:
                matching = self.get_matching(end)
                if len(matching) > 0:
                    # Draw the Domino from the hand and play it
                    play = self.draw(matching[0])
                    train.add_to_end(end, play)
                    return
        return

    def get_matching(self: Self, to_match: Domino) -> tuple[Domino]:
        """
        Returns all Dominoes in this Player's hand which match the given Domino.
        All returned Dominoes will be flipped so that their tops match the
        given Domino's bottom.
        """
        return super().all_matching(to_match)

    def clear(self: Self) -> int:
        """
        Removes all Dominoes from the Player's hand.
        Returns the sum of the removed Dominoes' point values.
        """
        output = 0
        while len(self.dominoes) > 0:
            output += self.draw_random().value()
        return output


class Train(DominoTree):
    """
    A Train of Dominoes in a game of Train Dominoes.
    The first Domino matches the Game's engine Domino,
    and each Domino matches the Domino before it in sequence.
    """

    def __init__(self: Self, player: Player, engine: Domino) -> None:
        super().__init__()
        self.player = player
        self.engine = engine
        self.marked = False

    def __str__(self) -> str:
        return f"Train(player={self.player.name}, marked={self.marked})"

    def __repr__(self) -> str:
        return f"Train(player={self.player.name}, marked={self.marked}, ends={list(self.ends.keys())})"

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
        super().__init__(Player(COMMUNITY_TRAIN), engine)
        self.marked = True

    def is_marked(self: Self) -> bool:
        return True

    def set_marked(self: Self) -> None:
        raise Exception("Cannot mark the community Train.")

    def set_unmarked(self: Self) -> None:
        raise Exception("Cannot un-mark the community Train.")


GameHash = tuple[tuple[Player, tuple[Domino]]]
"""
A hashable representation of a Game state.
Hash scheme: tuple(Player, tuple(Train ends)) for each Player and the C.T.\n
Sort Trains by Player name ascending, then the community Train at the end
"""


class Game:
    """
    A playable game of Train Dominoes.
    """

    def __init__(self: Self, player_names: Collection[str]) -> None:
        """
        Creates a new Game of Train Dominoes.
        """
        # Initialize our round counter to 0
        self.round_counter = 0

        # Create the Players in our Game, all starting with a score of 0
        name_set = set(player_names)
        if len(player_names) != len(name_set):
            raise Exception(
                f"Non-unique list of names provided to Game: {player_names}."
            )
        else:
            self.players = [Player(name) for name in player_names]
            self.rankings = {player: 0 for player in self.players}

        # Set the highest possible Domino side value and the starting Hand size
        self.SIDE_MAX, self.HAND_SIZE = get_domino_parameters(len(name_set))

        # Initialize the "engine" Domino that will start every round
        self.ENGINE = Domino(self.SIDE_MAX, self.SIDE_MAX)
        return

    def generate_dominoes(self: Self) -> DominoSet:
        """
        Generates a complete DominoSet.
        Valid Dominoes comprise all 2-element combinations of integers in the range [SIDE_MIN, self.SIDE_MAX].
        """
        dominoes = DominoSet([])
        for i in range(SIDE_MIN, self.SIDE_MAX + 1):
            for j in range(i, self.SIDE_MAX + 1):
                dominoes.add(Domino(i, j))
        return dominoes

    def play(self: Self) -> list[tuple[Player, int]]:
        """
        Play this Game to completion.
        Returns the scoreboard as a list of Player, score tuples in ascending score order.
        """
        while self.round_counter < MAX_ROUNDS:
            print(f"Setting up round {self.round_counter + 1}.")
            self.setup_round()

            # Play each Players' first turn
            self.play_first_turn()

            # Play subsequent turns for each Player
            while True:
                current_player = next(self.turn_order)

                print(f"Playing turn for Player {current_player.name}.")

                # The Player will play if they are able
                moved = self.attempt_move(current_player)

                # If the boneyard is empty, the Player is skipped
                if not moved and len(self.boneyard) > 0:
                    print("Player could not move, drawing from the boneyard.")
                    current_player.add(self.boneyard.draw_random())
                    moved = self.attempt_move(current_player)
                    print(f"Player drew a{' ' if moved else 'n un-'}playable Domino.")
                else:
                    print("Player was able to play a Domino.")

                # If the current Player has no more Dominoes, the round is over
                if len(current_player) == 0:
                    print(
                        f"Player {current_player.name} has no more Dominoes, so the round is over."
                    )
                    break

                print("\n\n")

            self.score_round()
            self.round_counter += 1

        return sorted(
            [(player, score) for player, score in self.rankings.items()],
            key=lambda x: x[1],
        )

    def setup_round(self: Self) -> None:
        """
        Sets up a new round of this Game.
        """
        # Generate a set of dominoes
        self.boneyard = self.generate_dominoes()

        # Pick the "engine" domino out from the boneyard
        self.boneyard.draw(self.ENGINE)

        # Deal out the appropriate number of Dominoes to each Player
        for player in self.players:
            for _ in range(self.HAND_SIZE):
                player.add(self.boneyard.draw_random())

        # Randomly pick a Player to play first
        self.turn_order = self.player_order(choice(self.players))

        # Player -> Train map
        self.trains = {player: Train(player, self.ENGINE) for player in self.players}

        # Set up the public "community" train
        self.community_train = CommunityTrain(self.ENGINE)
        return

    def score_round(self: Self) -> None:
        """
        Calculates player scores for the currently completed round.
        After scores are applied to the scoreboard, clears the Game board.
        """
        for player in self.players:
            self.rankings[player] += player.clear()
        return

    def player_order(self: Self, first_player: Player) -> Iterator[Player]:
        """
        An iterator which yields the next Player in the turn order.
        """
        current_idx = self.players.index(first_player)

        while True:
            yield self.players[current_idx]
            current_idx = (current_idx + 1) % len(self.players)

    def get_playable_trains(self: Self, player: Player) -> list[DominoTree]:
        """
        Returns all Trains (as Trees) that a Player has access to play on.
        """
        output = [self.community_train]
        for train in self.trains.values():
            if train.player == player or train.is_marked():
                output.append(train)
        return output

    def play_first_turn(self: Self) -> None:
        """
        Play the first turn for each Player. Players can only attempt
        to start their own Train on their first turn.
        """
        played = 0

        while played < len(self.players):
            played += 1
            current_player = next(self.turn_order)
            train = self.trains[current_player]

            print(f"Playing first turn for player {current_player.name}.")

            # If the Player draws the "Golden" matching Domino, they must play it
            current_player.make_move([train])
            drawn = self.boneyard.draw_random()

            if drawn.matches(self.ENGINE) or drawn.matches_flipped(self.ENGINE):
                print("Player drew the Golden Domino.")
                train.add_to_end(self.ENGINE, drawn)
            else:
                print("Player could not move.")
                train.set_marked()
            
            print("\n\n")
        return

    def attempt_move(self: Self, player: Player) -> bool:
        """
        Ask the given Player to attempt a move.
        If the Player cannot move, their Train is marked as public.
        Returns whether the Player was able to move.
        If the Player attempts an illegal move, throws an `InvalidMoveException`.
        """
        playable_trains = self.get_playable_trains(player)
        could_move = self.can_move(player)
        prev_state = self.to_hashable()

        # Ask the Player to make a move
        player.make_move(playable_trains)
        played_train = self.did_move(prev_state)

        if played_train is None:
            # The player must move if they are able
            if could_move:
                raise InvalidMoveException(
                    f"Player {player.name} could have played a Domino but did not.",
                    prev_state,
                )
            else:
                # If the Player does not move, their Train is now public
                self.trains[player].set_marked()
        else:
            # The train that was played onto must either be marked or be the Player's
            if played_train.player != player and not played_train.is_marked():
                raise InvalidMoveException(
                    f"Player {player.name} cannot play onto unmarked Train {played_train}.",
                    prev_state,
                )

            # If the Player played onto their Train, it is now not public
            elif played_train.player == player:
                self.trains[player].set_unmarked()

        return played_train is not None

    def can_move(self: Self, player: Player) -> bool:
        """
        Whether there are any places that the given Player can play a Domino.
        """
        playable_trains = self.get_playable_trains(player)
        for train in playable_trains:
            if train.playable_ends(player.dominoes):
                return True
        return False

    def did_move(self: Self, prev: GameHash) -> Optional[Train]:
        """
        Whether there is a difference between the given Game state and
        the current Game state. Returns the Train that has been played onto,
        if one exists.
        """
        hashed_trains = iter(prev)

        # Check each of the player Trains, sorted by player name
        for _, train in sorted(self.trains.items(), key=lambda item: item[0].name):
            _, prev_ends = next(hashed_trains)
            _, new_ends = self.hash_train(train)
            if prev_ends != new_ends:
                return train

        # Check the community Train
        _, prev_comm_ends = next(hashed_trains)
        _, new_comm_ends = self.hash_train(self.community_train)
        if prev_comm_ends != new_comm_ends:
            return self.community_train

        return

    def to_hashable(self: Self) -> GameHash:
        """
        Returns a hashable representation of a Game.
        If any Players have played onto a Train, the new hash must be different.
        """
        trains = [self.hash_train(train) for train in self.trains.values()]
        trains.sort(key=lambda item: item[0].name)
        trains.append(self.hash_train(self.community_train))

        return tuple(trains)

    def hash_train(self: Self, train: Train) -> tuple[Player, tuple[Domino]]:
        """
        Returns a hashable representation of the Player and ends of a Train.
        """
        return train.player, sorted(train.playable_ends([]))

    def rollback(self: Self, prev: str) -> None:
        """
        Rolls back this Game to the provided previous state.
        """
        # FIXME: I think this should be done by the Error handler that will catch InvalidMoveExceptions :)
        # FIXME: also need a way to roll back the player turn order iterator :0
        raise NotImplementedError
