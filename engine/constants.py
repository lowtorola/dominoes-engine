# Dominoes
SIDE_MIN = 0


# Gameplay
MAX_ROUNDS = 10
COMMUNITY_TRAIN = "community_train"


def get_domino_parameters(player_count: int) -> tuple[int, int]:
    """
    Returns a tuple containing the highest Domino side value and the number
    of Dominoes each Player should be dealt given that a Game contains a certain
    number of Players.
    """
    if player_count < 2:
        raise Exception("Cannot play Train Dominoes with fewer than 2 players.")
    elif player_count <= 3:
        # For 2-3 players, use a double-9 set -- each player takes 8
        return 9, 8
    elif player_count <= 6:
        # For 4-6 players, use a double-12 set -- each player takes 12
        return 12, 12
    elif player_count <= 8:
        # For 7-8 players, use a double-12 set -- each player takes 10
        return 12, 10
    elif player_count <= 12:
        # For 9-12 players, use a double-15 set -- each player takes 11
        return 15, 11
    elif player_count <= 14:
        # For 13-14 players, use a double-18 set -- each player takes 11
        return 18, 11
    else:
        raise Exception("Cannot play Train Dominoes with greater than 14 players.")
