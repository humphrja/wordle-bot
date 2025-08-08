"""
Tests the bot's performance and compares it against two human baselines.
This involves loading the live responses data (or some historical collection of Wordle responses),
running the bot against these responses, and then comparing the bot's performance to that of human players.

A column should be added to the csv file for the version of the bot used in the test. The analysis script should be called to judge the performance of the bot.
"""

# For each date and solution in the live responses:
    # Call the wordle app and set the answer
    # Run the bot against the answer for an entire game loop

# Generate a first guess once and store
# Then use this as the first guess for each game, saving calculation time for equivalent scenarios

import pandas as pd
from app import WordleApp
from bot import WordleSolver
from time import time

from argparse import ArgumentParser

MAX_GUESSES = 6
FAIL_SCORE = 7

def output_result(solved: bool, score: int, soln: str, game_num: int, total_games: int):    
    if solved:
        print(f"[{game_num}/{total_games}] Bot solved '{soln}' in {score} guesses.")
    else:
        print(f"[{game_num}/{total_games}] Bot failed to solve '{soln}' within {MAX_GUESSES} guesses.")


def game_loop(app: WordleApp, soln: str, first_guess: str) -> tuple[bool, int]:
    """ Returns if the bot solved wordle, and the corresponding game score. """
    # Create a new bot for this game
    bot = WordleSolver()

    # Set the answer for the app
    try:
        app.set_answer(soln)
    except ValueError as e:
        # raise ValueError(e)
        print(f"Unexpected solution '{soln}': {e}")
        # Do not validate against expected word list
        app.set_answer(soln, validate=False)
        bot.wordle_list.possible_solutions = bot.wordle_list.all_guesses.copy()
    
    # Start the game loop
    guesses = []
    
    for n in range(MAX_GUESSES):
        if n == 0:
            guess = first_guess
        else:
            # Bot makes a guess
            guess = bot.make_guess()

        # App provides feedback
        solved, feedback = app.check_guess(guess)

        # Display result (Y/M/N) for yes/maybe/no
        guess_str = app.make_guess_str(guess, feedback)
        guesses.append(guess_str)
        for g in guesses:
            print(g)

        if solved:
            return True, n+1

        # Apply feedback to the bot
        bot.apply_feedback(guess, feedback)

    return False, FAIL_SCORE

if __name__ == "__main__":
    parser = ArgumentParser(description="Wordle Bot Benchmarking Script")
    parser.add_argument('--version', '-v', type=str, help="Version of the bot being tested", required=True)
    parser.add_argument('--test_case', '-t', type=str, help="Single solution word to test against (optional)", required=False, default=None)
    parser.add_argument('--first_guess', '-fg', type=str, help="First guess bot should maket (optional)", required=False, default=None)
    args = parser.parse_args()

    app = WordleApp()

    bot_scores = []
    start_time = time()

    if args.first_guess:
        first_guess = args.first_guess.upper()
        print(f"Using provided first guess: {first_guess}")
    else:
        print(f"Calculating first guess...")
        bot = WordleSolver()
        first_guess = bot.make_guess()
        print(f"First guess: {first_guess} ({time() - start_time:.2f} s)")

    if args.test_case:
        solved, score = game_loop(app, args.test_case, first_guess)
        output_result(solved, score, args.test_case, 1, 1)
        exit()

    # Load the live responses data
    game_history = pd.read_csv("data/benchmark_results.csv")
    game_history = game_history.iloc[:3] # Truncate if needed

    for i, soln in enumerate(game_history['solution']):
        solved, score = game_loop(app, soln, first_guess)

        output_result(solved, score, soln, i+1, len(game_history))

        bot_scores.append(score)

    elapsed_time = time() - start_time
    print(f"Total duration: {elapsed_time:.2f} s")

    if args.test_case is None:
        # Save the results to a CSV file
        game_history[f'bot_v{args.version}'] = bot_scores

        game_history.to_csv(f"data/benchmark_results_v{args.version}.csv", index=False)
