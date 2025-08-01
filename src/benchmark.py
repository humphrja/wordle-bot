"""
Tests the bot's performance and compares it against two human baselines.
This involves loading the live responses data (or some historical collection of Wordle responses),
running the bot against these responses, and then comparing the bot's performance to that of human players.

A column should be added to the csv file for the version of the bot used in the test. The analysis script should be called to judge the performance of the bot.
"""


# For each date and solution in the live responses:
    # Call the wordle app and set the answer
    # Run the bot against the answer for an entire game loop
