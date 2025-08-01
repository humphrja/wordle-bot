from app import WordleList, add_to_freq_dict

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

        return self.wordle_list.all_guesses.iloc[0, 0]  # Return the guess with the highest score
