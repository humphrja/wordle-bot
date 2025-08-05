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

if __name__ == "__main__":
    parser = ArgumentParser(description="Wordle Bot Benchmarking Script")
    parser.add_argument('--version', '-v', type=str, help="Version of the bot being tested", required=True)
    args = parser.parse_args()

    # Load live-responses data
    game_history = pd.read_csv("data/benchmark_results.csv")
    game_history = game_history.iloc[:] # Truncate if needed

    max_guesses = 6
    fail_score = 7

    app = WordleApp()

    bot_scores = []
    bot = WordleSolver()

    start_time = time()

    print(f"Calculating first guess...")
    first_guess = bot.make_guess()
    print(f"First guess: {first_guess} ({time() - start_time:.2f} s)")

    for i, soln in enumerate(game_history['solution']):
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
        
        for _ in range(max_guesses):
            if len(guesses) == 0:
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
                break

            # Apply feedback to the bot
            bot.apply_feedback(guess, feedback)

        if solved:
            score = len(guesses)
            print(f"[{i+1}/{len(game_history)}] Bot solved '{soln}' in {score} guesses.")
        else:
            score = fail_score   # Strongly penalise failed solves
            print(f"[{i+1}/{len(game_history)}] Bot failed to solve '{soln}' within {max_guesses} guesses.")

        bot_scores.append(score)

    elapsed_time = time() - start_time
    print(f"Total duration: {elapsed_time:.2f} s")

    # Save the results to a CSV file
    game_history[f'bot_v{args.version}'] = bot_scores

    game_history.to_csv(f"data/benchmark_results_v{args.version}.csv", index=False)
