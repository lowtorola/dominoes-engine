from typing import Collection, Iterator, Optional
from engine.constants import *
from engine.models.domino import Domino, DominoTree, DominoSet
from engine.models.exceptions import InvalidMoveException
from typing_extensions import Self
from random import shuffle, choice
from engine.models.player import BotPlayer, HumanPlayer, Player
from engine.models.train import CommunityTrain, Train


GameHash = tuple[tuple[str, tuple[Domino]]]
"""
A hashable representation of a Game state.
Hash scheme: tuple(Player name, tuple(Train ends)) for each Player and the C.T.\n
Sort Trains by Player name ascending, then the community Train at the end
"""


class Game:
    """
    A playable game of Train Dominoes.
    """

    def __init__(self: Self, bot_count: int, human_player_names: Collection[str]) -> None:
        """
        Creates a new Game of Train Dominoes.
        """
        # Initialize our round counter to 0
        self.round_counter = 0

        # Create the Human Players in our Game (all Players start with a score of 0)
        name_set = set(human_player_names)
        if len(human_player_names) != len(name_set):
            raise Exception(
                f"Non-unique list of names provided to Game: {human_player_names}."
            )
        
        # Create the Bot Players
        self.players: list[Player] = [HumanPlayer(name) for name in human_player_names]
        for i in range(1, bot_count+1):
            bot_name = f"BotPlayer{i}"
            self.players.append(BotPlayer(bot_name))
            name_set.add(bot_name)
        
        # Randomize our player order
        shuffle(self.players)

        # Create the rankings for our game
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

    def play_next_round(self: Self) -> None:
        """
        Play the next round of this Game to completion.
        If this Game is over, raises an Exception.
        """
        if self.is_completed():
            raise Exception("Cannot play another round of completed Game.")
        else:
            # Set up this round
            print(f"Setting up round {self.round_counter + 1}.")
            self.setup_round()

            # The first turn has special rules
            self.play_first_turn()

            # Play until a Player runs out of Dominoes
            while True:
                current_player, turn_number = next(self.turn_order)
                print(f"Playing turn {turn_number} for Player {current_player.name}.")

                # If they cannot play, they must draw from the boneyard
                if not self.can_move(current_player):
                    print(f"Player could not move.")
                    if len(self.boneyard) > 0:
                        print(f"Drawing from boneyard.")
                        current_player.add(self.boneyard.draw_random())
                    else:
                        print("Boneyard is empty, skipping turn.")
                
                # Now, if they cannot play, mark their Train
                moved = self.attempt_move(current_player)
                if not moved:
                    print(f"Player {current_player.name}'s Train is now marked.")

                # If the current Player has no more Dominoes, the round is over
                if len(current_player) == 0:
                    print(
                        f"Player {current_player.name} has no more Dominoes, so the round is over."
                    )
                    break

            self.score_round()
            self.round_counter += 1
            return
        
    def format_rankings(self: Self) -> str:
        """
        Returns a formatted string representation of the rankings of this Game.
        """
        ordered = sorted(
            [(player, score) for player, score in self.rankings.items()],
            key=lambda x: x[1],
        )

        return "Rankings:\n" + "\n".join(
            f" {idx+1}. {player_score[0]} - {player_score[1]}" for idx, player_score in enumerate(ordered)
        )

    def is_completed(self: Self) -> bool:
        """
        Whether this Game has been completed.
        """
        return self.round_counter >= MAX_ROUNDS
    
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
        self.trains = {player: Train(player.name, self.ENGINE) for player in self.players}

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

    def player_order(self: Self, first_player: Player) -> Iterator[tuple[Player, int]]:
        """
        An iterator which yields a tuple of the next Player in the turn order,
        as well as their turn count for the current round.
        """
        count = 0
        current_idx = self.players.index(first_player)

        while True:
            yield self.players[current_idx], (count // len(self.players)) + 1
            current_idx = (current_idx + 1) % len(self.players)
            count += 1
    
    def get_playable_trains(self: Self, player: Player) -> list[DominoTree]:
        """
        Returns all Trains (as Trees) that a Player has access to play on.
        """
        output = [self.community_train]
        for train in self.trains.values():
            if train.player_name == player.name or train.is_marked():
                output.append(train)
        return output
    
    def play_first_turn(self: Self, player: Player) -> None:
        """
        Play the first turn for a given Player. Players can only attempt
        to start their own Train on their first turn.
        """
        train = self.trains[player]

        # If the Player can't move, they must draw
        if not self.can_move(player):
            print("Player has no move available. Drawing from the boneyard.")
            player.add(self.boneyard.draw_random())
        
        # If they still can't move, mark their Train
        if not self.can_move(player):
            print("Player has no first turn move! Marking their train.")
            train.set_marked()
        else:
            # The Player must move
            prev = self.to_hashable()
            player.make_move([train])
            moved = self.did_move(prev)
            if moved is None:
                raise InvalidMoveException(f"Expected player {player.name} to play onto their train.")
            else:
                print(f"Player played onto {str(train)}")
        return

    def play_turn(self: Self, player: Player, turn_number: int) -> None:
        """
        Play a turn for the given Player.
        """
        print(f"Playing turn {turn_number} for Player {player.name}.")

        # The first turn has special rules
        if turn_number == 1:
            return self.play_first_turn(player)

        # If they cannot play, they must draw from the boneyard
        if not self.can_move(player):
            print(f"Player could not move.")
            if len(self.boneyard) > 0:
                print(f"Drawing from boneyard.")
                player.add(self.boneyard.draw_random())
            else:
                print("Boneyard is empty, skipping turn.")
        
        # Now, if they cannot play, mark their Train
        moved = self.attempt_move(player)
        if not moved:
            print(f"Player {player.name}'s Train is now marked.")

        return


    # def play_first_turn(self: Self) -> None:
    #     """
    #     Play the first turn for each Player. Players can only attempt
    #     to start their own Train on their first turn.
    #     """
    #     played = 0

    #     while played < len(self.players):
    #         played += 1
    #         current_player, _ = next(self.turn_order)
    #         train = self.trains[current_player]

    #         print(f"Playing first turn for player {current_player.name}.")

    #         # If the Player can't move, they must draw
    #         if not self.can_move(current_player):
    #             print("Player has no move available. Drawing from the boneyard.")
    #             current_player.add(self.boneyard.draw_random())
            
    #         # If they still can't move, mark their Train
    #         if not self.can_move(current_player):
    #             print("Player has no first turn move! Marking their train.")
    #             train.set_marked()
    #         else:
    #             # The Player must move
    #             prev = self.to_hashable()
    #             current_player.make_move([train])
    #             moved = self.did_move(prev)
    #             if moved is None:
    #                 raise InvalidMoveException(f"Expected player {current_player.name} to play onto their train.")
    #             else:
    #                 print(f"Player played onto {str(train)}")
    #     return

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
            if played_train.player_name != player.name and not played_train.is_marked():
                raise InvalidMoveException(
                    f"Player {player.name} cannot play onto unmarked Train {played_train}.",
                    prev_state,
                )

            # If the Player played onto their Train, it is now not public
            elif played_train.player_name == player.name:
                self.trains[player].set_unmarked()

            print(f"Player played onto {str(played_train)}")

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
        trains.sort(key=lambda item: item[0])
        trains.append(self.hash_train(self.community_train))

        return tuple(trains)

    def hash_train(self: Self, train: Train) -> tuple[str, tuple[Domino]]:
        """
        Returns a hashable representation of the Player and ends of a Train.
        """
        return train.player_name, sorted(train.playable_ends([]))

    def rollback(self: Self, prev: str) -> None:
        """
        Rolls back this Game to the provided previous state.
        """
        # FIXME: I think this should be done by the Error handler that will catch InvalidMoveExceptions :)
        # FIXME: also need a way to roll back the player turn order iterator :0
        raise NotImplementedError