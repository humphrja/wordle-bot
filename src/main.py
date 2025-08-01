"""
Entry point for the program.
Contains the main game loop and handles user input.
This script allows the user to play Wordle in a terminal or have the bot solve it.
"""

from app import WordleApp
from bot import WordleSolver

from argparse import ArgumentParser
import colorama as cm


# Play mode:
    # No assistance: Wordle clone at the command line
    # Some assistance: Wordle clone with possible remaining words displayed
    # Full assistance: Best guesses displayed
    # Automatic: Bot plays for you

# Solve mode:
    # No assistance: user can enter guesses to get statistical feedback
    # Some assistance: Augmented wordle solving to show user possible solutions
    # Full assistance: Best guesses displayed
    # Automatic: Still need to wait for feedback to be input


if __name__ == '__main__':
    parser = ArgumentParser(description="Wordle Bot Command Line Options")
    parser.add_argument('--mode', type=str, help="Mode of operation: 'play' to play Wordle in the terminal, 'solve' to help a user play Wordle", choices=['play', 'solve'], required=True)
    parser.add_argument('--assistance', type=str, help="How much help is provided: 'full' to make guesses, 'some' to display possible words, or 'none'", choices=['full', 'some', 'none'], required=False, default='none')
    args = parser.parse_args()

    print(f"Welcome to the Wordle App! Running in {args.mode} mode... Assistance is set to {args.assistance}.\n")

    app = WordleApp()

    if args.mode == 'play':
        # Play mode: User plays Wordle against the bot
        print("You are playing Wordle! Enter your guesses and the app will provide feedback.")

        # Get app to generate a random solution
        app.generate_answer()
        print(f"Today's answer is: " + cm.Fore.BLACK + app.answer_chars + cm.Style.RESET_ALL + " (hidden)" )

    elif args.mode == 'solve':
        # # Solver mode: Bot solves the Wordle
        # soln = input("The bot will solve a Wordle challenge. Enter the solution word for the bot to solve against: ")
        # try:
        #     app.set_answer(soln)
        # except ValueError as e:
        #     print(e)
        #     exit()
        pass

    else:
        print("Invalid mode selected. Exiting.")
        exit()

    bot = WordleSolver()

    max_guesses = 6
    guesses = []
    soln_sets = []
    while len(guesses) < 6:
        # Solver makes guess

        if len(guesses) >= 1:
            # Guesses saree...
            bot.make_guess()

        guess = input("Guess: ")
        # Validate but don't be stupid and enter something wrong

        if args.mode == 'play':        
            # App provides feedback
            solved, feedback = app.check_guess(guess)
        elif args.mode == 'solve':
            feedback = input("Enter feedback for the guess (Y for yes, M for maybe, N for no): ").upper()
            if len(feedback) != len(guess) or any(c not in 'YMN' for c in feedback):
                print("Invalid feedback. Please enter a string of Y, M, N characters of the same length as the guess.")
                continue

            if feedback == 'Y' * len(guess):
                solved = True
            else:
                solved = False

        # Display result (Y/M/N) for yes/maybe/no
        guess_str = app.make_guess_str(guess, feedback)
        guesses.append(guess_str)
        for g in guesses:
            print(g)

        if solved:
            break
        
        # Solver adjusts possible guesses
        bot.apply_feedback(guess, feedback)

        # Future: Store list of possible solutions at each guess and display at the end to the user
        soln_sets.append(bot.wordle_list.possible_solutions.copy())

        if args.assistance != 'none':
            # Print remaining possible solutions
            print(f"Remaining possible solutions: {len(bot.wordle_list.possible_solutions)}")
            print(bot.wordle_list.possible_solutions)

            if args.assistance == 'full':
                # Display the best guess
                pass
        
        print("")

    if solved:
        print(f"Today's challenge has been solved in {len(guesses)} guesses!")
    else:
        print(f"Today's challenge could not be solved.")

        if args.mode == 'play':
            print(f"The answer was {app.answer_chars}")

    if args.assistance == 'none':
        print("\nPossible solutions at each guess:")
        for i, (guess, soln_set) in enumerate(zip(guesses, soln_sets)):
            print(f"After guess {i+1} - {guess}: {len(soln_set)} possible solutions")
            print(soln_set)

            # Also print what ranking the guess was


    print(cm.Style.RESET_ALL)