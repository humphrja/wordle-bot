"""
Script to analyse the performance of Wordle competitors.

This has already been implemented in an excel spreadsheet. However, automating this in Python would enable the integration of the bot's results and compare it with humans.
"""

import pandas as pd
import matplotlib.pyplot as plt

import argparse

# Guesses should be stored a csv file with the following columns:
# - 'date': The date of the puzzle
# - 'solution': The solution to the puzzle
# - 'player-a-guesses': The guesses made by player A
# - 'player-b-guesses': The guesses made by player B
# ...





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wordle Bot Analysis Script")
    parser.add_argument('--file', '-f', type=str, help="Data file containing player scores", required=True)
    args = parser.parse_args()

    # Load the data
    player_scores = pd.read_csv(f"data/{args.file}.csv")
    # Set date as index
    player_scores.set_index('date', inplace=True)

    scores = player_scores.drop(columns=['solution'])
    means = scores.mean()
    print(means)

    # Filter rows where any player's guesses are greater than 6
    failures = player_scores[scores.gt(6).any(axis=1)]
    print(failures)

    # Calculate a 7-day rolling average for each player (excluding 'solution' column)
    rolling_avg = scores.rolling(window=7).mean()
    print(rolling_avg)

    fig, ax = plt.subplots(figsize=(10, 6))
    
    lines = ax.plot(rolling_avg)
    legend1 = ax.legend(lines, rolling_avg.columns, loc='upper left')
    ax.add_artist(legend1)  # Add the first legend to the plot

    # Add horizontal lines representing means, with same color as the player line
    for player, line in zip(rolling_avg.columns, lines):
        ax.axhline(y=means[player], color=line.get_color(), linestyle='--', label=f'{player} Mean')

    legend2 = ax.legend([plt.Line2D(xdata=[], ydata=[], color='black', linestyle='--')], ["mean"], loc='upper right')
    ax.add_artist(legend2)  # Add the second legend to the plot

    # # Add vertical lines for failures
    # for date in failures.index:
    #     plt.axvline(x=date, color='red', linestyle=':', label='Failure')


    ax.set_title('Average Number of Guesses per Player')
    ax.set_xlabel('Date')
    ax.set_ylabel('Weekly Rolling Average')
    # plt.show()
    fig.savefig(f"data/{args.file}_analysis.png")