from constants import *
import random

class Domino():
  def __init__(self, sides):
    self.sides = sides
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

class DominoSet():
  def __init__(self, dominoes):
    self.dominoes = dominoes

  """
  Picks a random Domino from the set.
  """
  def pick_random(self):
    return random.choice(self.dominoes)

class Train():
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

class Player():
  """
  Create a new Player with a DominoSet hand and a name.
  """
  def __init__(self, hand, name):
    self.hand = hand
    self.name = name

  """
  Plays a domino from the player's hand to the train if it fits.
  Returns true if the move is successful, false otherwise.
  """
  def make_move(self, domino, train):
    if train.fits_at_end(domino):
      train.dominoes.append(domino)
      self.hand.dominoes.remove(domino)
      return True
    return False
  
  """
  Sums all domino sides in the player's hand.
  """
  def calculate_score(self):
    return sum([sum(domino.sides) for domino in self.hand.dominoes])
  
  """
  Takes in a Game object and checks all possible locations for a valid move.
  Returns true if a valid move exists, false otherwise.
  """
  def has_valid_move():
    raise NotImplementedError

class Game():
  """
  Creates a new game given a list of player names.
  """
  def __init__(self, players):
    pass

  """
  Generates a new set of dominoes.
  Returns all 2-element combinations of integers from 0 to 12 in a set.
  """
  def generate_dominoes(self):
    dominoes = set()
    for i in range(SIDE_MIN, SIDE_MAX + 1):
      for j in range(i, SIDE_MAX + 1):
        dominoes.add(Domino((i, j)))
    return dominoes

