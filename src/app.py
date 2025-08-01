import pandas as pd
from collections import Counter
import colorama as cm

class WebScraper:
    # In future, web scrape to retrieve this
    def get_answer_from_web(self) -> str:
        # Web scrape code here?
        # Or look at list of words and use today's date...
        return ""

# def create_freq_dict(word: str) -> dict[str,int]:
#     # freq_dict = {}
#     # for char in word:
#     #     add_to_freq_dict(char, freq_dict)

#     return Counter(word)

    # return freq_dict

def add_to_freq_dict(char, freq_dict):
    if char in freq_dict:
        freq_dict[char] += 1
    else:
        freq_dict[char] = 1


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
        self.char_freq = Counter(self.answer_chars)

    def generate_answer(self):
        # Randomly select a word from the list of possible solutions
        self.answer_chars = self.wl.possible_solutions.sample(n=1).iloc[0, 0].upper()
        self.char_freq = Counter(self.answer_chars)

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