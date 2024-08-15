from engine.constants import SIDE_MIN, SIDE_MAX
from engine.models.domino import Domino, DominoSet
from engine.models.player import Player


class Game:
    """
    The representation of a game of Train Dominoes.
    """

    def __init__(self, players):
        """
        Creates a new game state given a list of player names.
        """
        # # The round number is the side of the double that starts the round.
        # self.round = SIDE_MAX
        # dominoes = self.generate_dominoes()
        # self.middle = Domino((SIDE_MAX, SIDE_MAX))
        # dominoes.discard(self.middle)

        # # Deal the dominoes into len(players) hands of 12 dominoes each and a boneyard.
        # self.boneyard = DominoSet(dominoes)
        # self.trains = {
        #     player: Train([self.middle], Player(set(), player), True)
        #     for player in players
        # }
        # # The free train has no player and is always playable.
        # self.trains.update({"FREE": Train([self.middle], None, True)})
        # for _ in range(SIDE_MAX):
        #     for player in players:
        #         random_domino = self.boneyard.pick_random()
        #         self.trains[player].player.hand.add(random_domino)
        #         self.boneyard.dominoes.discard(random_domino)
        raise NotImplementedError

    def generate_dominoes():
        """
        Generates a new set of dominoes.
        Returns all 2-element combinations of integers from 0 to 12 in a set.
        """
        # dominoes = set()
        # for i in range(SIDE_MIN, SIDE_MAX + 1):
        #     for j in range(i, SIDE_MAX + 1):
        #         dominoes.add(Domino((i, j)))
        # random.shuffle(dominoes)
        # return dominoes
        raise NotImplementedError