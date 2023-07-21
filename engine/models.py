from engine.constants import *
import random


class Domino:
    def __init__(self, sides):
        self.sides = sides

    def __eq__(self, other):
        return all(side in other for side in self.sides)

    """
  Flips the domino.
  """

    def flip(self):
        self.sides = (self.sides[1], self.sides[0])

    """
  Returns a flipped copy of the domino.
  """

    def flipped(self):
        return Domino((self.sides[1], self.sides[0]))


class DominoSet:
    def __init__(self, dominoes):
        self.dominoes = dominoes

    """
  Picks a random Domino from the set.
  """

    def pick_random(self):
        return random.choice(self.dominoes)


class Train:
    player = None
    has_train = False

    def __init__(self, dominoes, player=None, has_train=None):
        self.dominoes = dominoes
        self.player = player
        self.has_train = has_train

    """
  Returns true if the domino fits at the end of the train.
  If the domino fits once it is flipped, it is flipped.
  """

    def fits_at_end(self, domino):
        if self.dominoes[-1][1] == domino.sides[0]:
            return True
        flipped_copy = domino.flipped()
        if self.dominoes[-1][1] == flipped_copy.sides[0]:
            domino.flip()
            return True
        return False


class Player:
    """
    Represents a player in a game of Train Dominoes.
    """

    def __init__(self, hand, name):
        """
        Create a new Player with a DominoSet hand and a name.
        """
        self.hand = hand
        self.name = name

    def make_move(self, domino, train):
        """
        Plays a domino from the player's hand to the train if it fits.
        Returns true if the move is successful, false otherwise.
        """
        if train.fits_at_end(domino):
            train.dominoes.append(domino)
            self.hand.dominoes.remove(domino)
            return True
        return False

    def calculate_score(self):
        """
        Sums all domino sides in the player's hand.
        """
        return sum([sum(domino.sides) for domino in self.hand.dominoes])

    def has_valid_move():
        """
        Takes in a Game object and checks all possible locations for a valid move.
        Returns true if a valid move exists, false otherwise.
        """
        raise NotImplementedError


class Game:
    """
    The representation of a game of Train Dominoes.
    """

    def __init__(self, players):
        """
        Creates a new game state given a list of player names.
        """
        # The round number is the side of the double that starts the round.
        self.round = SIDE_MAX
        dominoes = self.generate_dominoes()
        self.middle = Domino((SIDE_MAX, SIDE_MAX))
        dominoes.discard(self.middle)

        # Deal the dominoes into len(players) hands of 12 dominoes each and a boneyard.
        self.boneyard = DominoSet(dominoes)
        self.trains = {
            player: Train([self.middle], Player(set(), player), True)
            for player in players
        }
        # The free train has no player and is always playable.
        self.trains.update({"FREE": Train([self.middle], None, True)})
        for _ in range(SIDE_MAX):
            for player in players:
                random_domino = self.boneyard.pick_random()
                self.trains[player].player.hand.add(random_domino)
                self.boneyard.dominoes.discard(random_domino)

    def generate_dominoes():
        """
        Generates a new set of dominoes.
        Returns all 2-element combinations of integers from 0 to 12 in a set.
        """
        dominoes = set()
        for i in range(SIDE_MIN, SIDE_MAX + 1):
            for j in range(i, SIDE_MAX + 1):
                dominoes.add(Domino((i, j)))
        random.shuffle(dominoes)
        return dominoes
