from engine.models.game import Game


def clear_terminal() -> None:
    """
    Clears the terminal.
    """
    # TODO how to do this frfr halppp
    print("\n" * 20)
    return


def round_display(game: Game) -> None:
    """
    Prints a wonderful, beautiful display for the current Game to play in :)
    """
    # TODO something like the current round, MAYBE the board state, etc.?
    hand_sizes = sorted(
        [(len(player.dominoes), player.name) for player in game.players]
    )
    print(f"Round {game.round_counter + 1}:")
    print(
        f"Player hand sizes:\n"
        + "\n".join([f"{name}: {hand_size}" for hand_size, name in hand_sizes])
    )
    print("\n\n")
    return


if __name__ == "__main__":
    # Welcome user to the game
    print("Welcome to Train Dominoes! TODO rules explanation flag here :)\n")

    # Player count/name setup
    bot_count = int(input("Please enter the desired number of CPU players: "))
    human_count = int(input("Please enter the desired number of human players: "))
    humans: list[str] = []
    for i in range(1, human_count + 1):
        humans.append(input(f"Please enter a unique name for human player {i}: "))

    # Create Game
    game = Game(bot_count, humans)

    # Start Game
    while not game.is_completed():
        # Set up the next round
        print(f"Setting up round {game.round_counter + 1}.")
        game.setup_round()

        # Play until the round is completed
        while True:
            # Print our lovely terminal header
            clear_terminal()
            round_display(game)

            current_player, turn_number = next(game.turn_order)
            game.play_turn(current_player, turn_number)

            # If the current Player has no more Dominoes, the round is over
            if len(current_player) == 0:
                print(
                    f"Player {current_player.name} has no more Dominoes, so the round is over."
                )
                break
        
        game.score_round()
        game.round_counter += 1

    # Print rankings
    clear_terminal()
    print("Game over! Thanks for playing! :)")
    print(game.format_rankings())
