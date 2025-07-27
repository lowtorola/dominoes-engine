from typing import Any
from typing_extensions import Self
from engine.models.domino import Domino, DominoSet
from engine.models.exceptions import InvalidMoveException
from engine.models.train import Train


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

    def make_move(self: Self, playable_trains: list[Train]) -> None:
        """
        Plays a move for this Player onto one of the Trains.
        If the Player cannot move, they will do nothing.
        """
        raise Exception("This Player is generic and has no strategy.")

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


class BotPlayer(Player):
    """
    A computer-controlled Player in a Game of Train Dominoes.
    """

    def make_move(self: Self, playable_trains: list[Train]) -> None:
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


class HumanPlayer(Player):
    """
    A human-controlled (through the Game interface) Player in a Game of Train Dominoes.
    """

    def make_move(self: Self, playable_trains: list[Train]) -> None:
        if len(playable_trains) == 0:
            raise Exception(
                "Expected Players to always at least be able to play on their own Train."
            )

        # Set up Domino and Train number maps
        ordered_dominoes = {idx + 1: domino for idx, domino in enumerate(self.dominoes)}
        ordered_trains = {
            idx + 1: train
            for idx, train in enumerate(
                filter(
                    lambda train: len(train.playable_ends(self.dominoes)) > 0,
                    playable_trains,
                )
            )
        }

        # Print out the Player's hand
        print(f"It is your turn, {self.name}! Your hand is:")
        # TODO have several columns of dominoes
        for idx, domino in ordered_dominoes.items():
            print(f"{idx}: {str(domino)}")

        # Choose a Train to play on
        if len(ordered_trains) == 0:
            return
        elif len(ordered_trains) == 1:
            chosen_train = ordered_trains.pop(1)
            print(f"The only train you can play on is {str(chosen_train)}.")
        else:
            # Print out the ends of the Player's playable Trains
            print("Playable Trains:")
            for idx, train in ordered_trains.items():
                print(f"{idx}: ({str(train)}) -> {train.get_ends()}")

            chosen_train = ordered_trains[
                int(
                    input(
                        "Please enter the number of the Train you'd like to play on: "
                    )
                )
            ]

        # Choose an end of the Train
        ordered_ends = {
            idx + 1: end
            for idx, end in enumerate(chosen_train.playable_ends(self.dominoes))
        }
        if len(ordered_ends) == 1:
            chosen_end = ordered_ends.pop(1)
            print(f"The only train end you can play on is {str(chosen_end)}.")
        else:
            # Print the ends of the Train
            print(f"You are playing on {str(chosen_train)}. Here are its ends:")
            for idx, end in ordered_ends.items():
                print(f"{idx}: {end}")

            chosen_end = ordered_ends[
                int(
                    input(
                        "Please enter the number of the end you'd like to play on: "
                    )
                )
            ]

        # Choose a Domino to play
        chosen_domino = ordered_dominoes[
            int(
                input(
                    "Please enter the number of the Domino you'd like to play: "
                )
            )
        ]

        # Draw the Domino from the hand and play it
        play = self.draw(chosen_domino)
        chosen_train.add_to_end(chosen_end, play)
        return

        # TODO handle cases where the player can only play on 0/1 end/train :)
        # TODO should either auto-handle or not prompt e.g. if there's only one end of the chosen train :)
        # TODO should have better formatting :)

        # while True:
        #     # Set up Domino and Train number maps
        #     ordered_dominoes = {
        #         idx + 1: domino for idx, domino in enumerate(self.dominoes)
        #     }
        #     ordered_trains = {
        #         idx + 1: train for idx, train in enumerate(playable_trains)
        #     }

        #     # Print out the Player's hand
        #     print(f"It is your turn, {self.name}! Your hand is:")
        #     # TODO have several columns of dominoes
        #     for idx, domino in ordered_dominoes.items():
        #         print(f"{idx}: {str(domino)}")

        #     # Print out the ends of the Player's playable Trains
        #     print("Playable Trains:")
        #     for idx, train in ordered_trains.items():
        #         print(f"{idx}: ({str(train)}) -> {train.get_ends()}")

        #     # TODO should we prompt for train first, then show only the dominoes which fit? probably!! :))
        #     # Prompt the user to enter their move
        #     try:
        #         chosen_train = ordered_trains[
        #             int(
        #                 input(
        #                     "Please enter the number of the Train you'd like to play on: "
        #                 )
        #             )
        #         ]
        #         ordered_ends = {
        #             idx + 1: end
        #             for idx, end in enumerate(chosen_train.playable_ends(self.dominoes))
        #         }

        #         # If this Train is not playable, restart
        #         if len(ordered_ends) == 0:
        #             print(
        #                 f"No playable ends on train {str(chosen_train)}. Please try again!\n\n"
        #             )
        #             continue

        #         # Print the ends of the Train
        #         print(f"You chose to play on {str(chosen_train)}. Here are its ends:")
        #         for idx, end in ordered_ends.items():
        #             print(f"{idx}: {end}")

        #         chosen_end = ordered_ends[
        #             int(
        #                 input(
        #                     "Please enter the number of the end you'd like to play on: "
        #                 )
        #             )
        #         ]
        #         chosen_domino = ordered_dominoes[
        #             int(
        #                 input(
        #                     "Please enter the number of the Domino you'd like to play: "
        #                 )
        #             )
        #         ]

        #         # Draw the Domino from the hand and play it
        #         play = self.draw(chosen_domino)
        #         train.add_to_end(chosen_end, play)
        #         return
        #     except InvalidMoveException:
        #         print("An error occurred! Please try to play again.\n\n")
        #         continue
