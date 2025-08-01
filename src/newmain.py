import pandas as pd
import colorama as cm
from collections import Counter
from argparse import ArgumentParser
import string

class WebScraper:
    # In future, web scrape to retrieve this
    def get_answer_from_web(self) -> str:
        # Web scrape code here?
        # Or look at list of words and use today's date...
        return ""
    

def add_to_freq_dict(char, freq_dict):
    if char in freq_dict:
        freq_dict[char] += 1
    else:
        freq_dict[char] = 1

def create_freq_dict(word: str) -> dict[str,int]:
    # freq_dict = {}
    # for char in word:
    #     add_to_freq_dict(char, freq_dict)

    return Counter(word)

    return freq_dict


class WordleList:
    def __init__(self):
        self.possible_solutions: pd.DataFrame
        self.all_guesses: pd.DataFrame

        # Load all the possible guesses and solutions into pandas dataframes
            # words.txt is the union of guesses.txt and solutions.txt
        with open("data/words.txt", "r") as file:
            # Create dataframe out of list of comma-separated strings, removing the quotation marks
            self.all_guesses = pd.DataFrame([guess.strip('"').upper() for guess in file.read().split(',')])

        with open("data/solutions.txt", "r") as file:
            # Create dataframe out of list of comma-separated strings, removing the quotation marks
            self.possible_solutions = pd.DataFrame([guess.strip('"').upper() for guess in file.read().split(',')])

        # Add a column to all_guesses that contains each guess' char freq
        # self.all_guesses['freq_dist'] = self.all_guesses[0].apply(create_freq_dict)


    # Exclude all solutions that contain char
        # Be careful about repeated letters that are yellow but have exceeded the frequency in the answer
    def filter_on_black(self, char: str):
        self.possible_solutions = self.possible_solutions[~self.possible_solutions[0].str.contains(char.upper())]
        # print(f"Filtered out all solutions containing {char}. Remaining solutions: {len(self.possible_solutions)}")
        # print(self.possible_solutions)
    
    # Select all solutions that have char at index
    def filter_on_green(self, char: str, index: int):
        self.possible_solutions = self.possible_solutions[self.possible_solutions[0].str[index] == char.upper()]
        # print(f"Filtered out all solutions that do not have {char} at index {index}. Remaining solutions: {len(self.possible_solutions)}")
        # print(self.possible_solutions)

    # Select all solutions that have char in word, but not at index
    def filter_on_yellow(self, char: str, index: int):
        self.possible_solutions = self.possible_solutions[self.possible_solutions[0].str.contains(char.upper())]
        self.possible_solutions = self.possible_solutions[self.possible_solutions[0].str[index] != char.upper()]
        # print(f"Filtered out all solutions that have {char} in the word, but not at index {index}. Remaining solutions: {len(self.possible_solutions)}")
        # print(self.possible_solutions)

    # This considers blacks that are technically yellows but with too many letters already
    # This index is not a green (which would have priority) so it definitely can't be a candidate for where the other yellows can go
    def filter_on_black_yellow(self, char: str, index: int):
        self.possible_solutions = self.possible_solutions[self.possible_solutions[0].str[index] != char.upper()]
        # print(f"Filtered out all solutions that don't have {char} at index {index}. Remaining solutions: {len(self.possible_solutions)}")
        # print(self.possible_solutions)

    def filter_on_frequency(self, char: str, freq: int):
        self.possible_solutions = self.possible_solutions[self.possible_solutions[0].str.count(char.upper()) == freq]
        # print(f"Filtered all solutions to those that have {char} exactly {freq} times. Remaining solutions: {len(self.possible_solutions)}")
        # print(self.possible_solutions)


# This contains the answer to the wordle
class WordleApp:
    def __init__(self):
        self.wl = WordleList()
        self.answer_chars = ""
        self.char_freq = {}  # Dictionary, where the key is the character, and the value is the number of times it has been checked

    def set_answer(self, answer: str):
        # Check answer is within the list of possible solutions
        if answer.upper() not in self.wl.possible_solutions[0].values:
            raise ValueError(f"Answer '{answer}' is not a valid solution.")

        self.answer_chars = answer.upper()
        self.char_freq = create_freq_dict(self.answer_chars)

    def generate_answer(self):
        # Randomly select a word from the list of possible solutions
        self.answer_chars = self.wl.possible_solutions.sample(n=1).iloc[0, 0].upper()
        self.char_freq = create_freq_dict(self.answer_chars)

    def load_answer(self):
        # Get the answer from the web
        return

       
    def check_guess(self, guess: str) -> tuple[bool, str]:
        guess = guess.upper()

        feedback = [None]*len(guess)

        # Dictionary, where the key is the character, and the value is the number of times it has been checked
        checked_chars = {}

        # Need to prioritise Greens over Yellows
        # e.g. guessing FFFXX against OFFER produces MYYNN, when it should actually produce NYYNN.
        # Consequence of iterating through linearly
        # Need to iterate through entire word just for greens
            # Then do second pass for yellows
            # Blacks here as well?

        # First pass
        for i, (guess_char, correct_char) in enumerate(zip(guess, self.answer_chars)):
            # Black - not in word at all (or dict)
            if guess_char not in self.answer_chars:
                feedback[i] = 'N'
                add_to_freq_dict(guess_char, checked_chars)
        
            # Green
            elif guess_char == correct_char:
                feedback[i] = 'Y'
                add_to_freq_dict(guess_char, checked_chars)
            
        # Second pass
        for i, (guess_char, correct_char) in enumerate(zip(guess, self.answer_chars)):
            # Skip already checked letters
            if feedback[i] != None:
                continue

            # In word (in dict) (already checked)

            # Definitely yellow because it is the first occurrence
            if guess_char not in checked_chars:
                feedback[i] = 'M'

            # Yellow or Black - need to verify how many times it has already been checked vs how many occurrences are in the answer
                # i.e. the frequency of checked_chars hasn't yet hit the frequency in char_freq
            elif checked_chars[guess_char] < self.char_freq[guess_char]:
                # Still more possible letters that could be yellow
                feedback[i] = 'M'

            else:
                # More letters than there are in the word, so must be black instead of yellow/green
                feedback[i] = 'N'
                
            add_to_freq_dict(guess_char, checked_chars)

        solved = feedback == ['Y']*len(self.answer_chars)
        return solved, feedback
    
    def make_guess_str(self, guess, feedback) -> str:
        out_str = cm.Fore.BLACK
        for char_guess, char_feedback in zip(guess, feedback):
            if char_feedback == 'Y':
                out_str += cm.Back.GREEN
            elif char_feedback == 'M':
                out_str += cm.Back.YELLOW
            elif char_feedback == 'N':
                out_str += cm.Back.LIGHTBLACK_EX

            out_str += char_guess

        out_str += cm.Style.RESET_ALL
        return out_str



class WordleSolver:
    def __init__(self):
        self.wordle_list = WordleList()

        # Dictionary where key is a character, and values are a list of valid positions. Calculated from the remaining solutions        
        self.char_info = {}

    # Apply feedback to current guess list
    def apply_feedback(self, guess: str, feedback: str):
        guess = guess.upper()
        
        # Reduce size of possible solutions based on the feedback
        # This represents the characters within this current guess that are known to be in the word
        chars_in_word = {}

        # First pass on green (no ambiguity):
        for i, char in enumerate(guess):
            if feedback[i] == 'Y':
                self.wordle_list.filter_on_green(char, i)
                add_to_freq_dict(char, chars_in_word)

        # Second pass on yellow
            # Could this be done in the first pass? probably
        for i, char in enumerate(guess):
            if feedback[i] == 'M':
                self.wordle_list.filter_on_yellow(char, i)
                add_to_freq_dict(char, chars_in_word)

        # Third pass on black, considering letter frequencies

        # If a letter is black, it is either:
            # a) Not in the word at all
                # Always true when this is the first encounter of the letter
            # b) In the word, but we've already checked this letter enough times
                # i.e. the 
                # But I think this would just be the last case (else of above)

        # For a black letter
            # If it has not been checked before
                # Filter on black
            # If it has been checked before
                # Filter on black/yellow
                # This also tells us the frequency of that letter in the word

        for i, char in enumerate(guess):
            if feedback[i] == 'N':
                if char not in chars_in_word:
                    self.wordle_list.filter_on_black(char)
                else:
                    self.wordle_list.filter_on_black_yellow(char, i)
                    print(f"Frequency of {char} in solution: {chars_in_word[char]}")
                    self.wordle_list.filter_on_frequency(char, chars_in_word[char])

        # self.char_info = {}
        # # Use remaining solutions to populate char_info
        # for soln in self.wordle_list.possible_solutions[0]:
        #     for i, char in enumerate(soln):
        #         if char not in self.char_info:
        #             self.char_info[char] = []
        #         if i not in self.char_info[char]:
        #             self.char_info[char].append(i)

    # def char_freq_dot_product(self, guess_freq: dict, soln_char_freqs: dict) -> float:
    #     # Calculate the dot product of the guess frequency and the solution character frequencies
    #     return sum(guess_freq[char] * soln_char_freqs.get(char, 0) for char in guess_freq)
    # # Maybe this could work if it also considers which characters have already been guessed (past guesses + those attempted within the current guess being checked)
    
    # Returns a score for a given guess, by comparing it to each solution
    def score_guess(self, guess: str, possible_solutions: list[str]) -> float:
        # Loop through each solution
            # Compare characters
        score = 0
        MATCHING_SCORE = 1.0
        IN_WORD_SCORE = 0.5

        REPEATED_CHAR_PENALTY = 0.8

        # Account for repeated letters in the guess
        chars_checked = {}

        for soln in possible_solutions:
            # Check matching positions
                # Add 1
            # Check in word (and not matching)
                # Add 0.5

            for i, char in enumerate(guess):
                # Do not score characters that are definitely not in the word
                if char not in self.char_info:
                    continue
                if i not in self.char_info[char]:
                    continue




                if char in soln:
                    if char == soln[i]:
                        # Matching character at the same position
                        score += MATCHING_SCORE
                    else:
                        # Character is in the word, but not at the same position
                        score += IN_WORD_SCORE

                # # First check of character:
                # if char not in chars_checked:
                #     if char == soln[i]:
                #         score += MATCHING_SCORE
                #     elif char in soln:
                #         score += IN_WORD_SCORE

                #     chars_checked[char] = 1

                # else:
                #     if char == soln[i]:
                #         # Remove the score for IN_WORD_SCORE
                #         score -= IN_WORD_SCORE
                #         # score += MATCHING_SCORE
                #         score += MATCHING_SCORE * REPEATED_CHAR_PENALTY ** chars_checked[char]
                #     # Do not consider IN_WORD_SCORE again
                #     chars_checked[char] += 1

        # Should bench test this
        return score

    
    def make_guess(self) -> str:
        # Get freq distribution of characters in remaining solutions
        # all_chars = "".join(self.wordle_list.possible_solutions[0])
        # char_freqs = Counter(all_chars)
        # char_freqs_normalized = {char: freq / len(self.wordle_list.possible_solutions) for char, freq in char_freqs.items()}

        # Score all guesses by their dot product with the character frequencies of the remaining solutions
        # self.wordle_list.all_guesses['dot_product'] = self.wordle_list.all_guesses['freq_dist'].apply(lambda freq_dist: self.char_freq_dot_product(freq_dist, char_freqs_normalized))
        # self.wordle_list.all_guesses.sort_values(by='dot_product', ascending=False, inplace=True)

        # Score all guesses by their variance
        # Keep history of previous characters and their feedback/positions, and also of the current guess chars
            # This should be implied from the remaining solutions list


        self.char_info = {}
        # Use remaining solutions to populate char_info
        for soln in self.wordle_list.possible_solutions[0]:
            for i, char in enumerate(soln):
                if char not in self.char_info:
                    self.char_info[char] = []
                if i not in self.char_info[char]:
                    self.char_info[char].append(i)

        # Instead, use the positions of characters in the remaining solutions to determine the best guess
        self.wordle_list.all_guesses['score'] = self.wordle_list.all_guesses[0].apply(lambda guess: self.score_guess(guess, self.wordle_list.possible_solutions[0]))
        self.wordle_list.all_guesses.sort_values(by='score', ascending=False, inplace=True)

        # TODO:
        # Account for repeated letters when scoring each guess
        # If scores are equal, preference words that are actual possible solutions

        print(self.wordle_list.all_guesses)

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



