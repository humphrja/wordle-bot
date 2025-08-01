from playwright.sync_api import sync_playwright, Page
import time, random

# This code is almost exactly as left during the talk.
# I made 2 modifications, and they are marked with comments

def avoid_rules(page: Page):
    print("Avoiding rules...")
    # play_btn_class="Welcome-module_button__ZG0Zh Welcome-module_gameSaleStyle__duVA4"
    page.locator('game-help').click()
    # page.locator(play_btn_class).click()

def press_letter(page: Page, key):
    print(f"Pressing letter: {key}")
    page.locator(f'#keyboard button[data-key={key}]').click()

def guess_word(page: Page, word):
    for letter in word:
        press_letter(page, letter)
    press_letter(page, '↵')

def get_hints(page: Page, guess_num):
    rows = page.query_selector_all('game-row')
    tiles = rows[guess_num-1].query_selector_all('div.row game-tile')
    get_letter = lambda tile: tile.get_attribute('letter')
    get_evaluation = lambda tile: tile.get_attribute('evaluation')

    # the rest of this function was modified after talk
    # black letter doesn't always mean absent
    # if the correct word is "lists" and you guess "skill"
    # then the first "l" in skill is marked "present", and the second is "absent"

    hints = [(get_letter(tile), get_evaluation(tile)) for tile in tiles]

    # when we have contradictory hints, replace absent with overused
    # track all modifiers per letter
    letters = {i[0]: set() for i in hints}
    for hint in hints:
        letters[hint[0]].add(hint[1])

    should_replace_absent = lambda letter: len(letters[letter] - set(['absent'])) >= 1
    replace_absent = lambda hint: (hint[0], 'overused') if should_replace_absent(hint[0]) and hint[1] == 'absent' else hint

    modified_hints = list(map(replace_absent, hints))
    return modified_hints

def all_correct(page: Page, hints):
    if len(hints) == 0:
        return False
    return all([i[1] == 'correct' for i in hints[-1]])

def prune(words, all_hints):
    valid_words = [i for i in words]
    for guess_hints in all_hints:
        keep_correct = lambda word: all(
        [word[i] == guess_hints[i][0] for i in range(len(word)) if guess_hints[i][1] == 'correct'])

        exclude_absent = lambda word: all(i[0] not in word for i in guess_hints if i[1] == 'absent')

        # added this line after talk
        move_present = lambda word: all([word[i] != guess_hints[i][0] and guess_hints[i][0] in word for i in range(len(guess_hints)) if guess_hints[i][1] == 'present'])

        # added move_present after talk
        is_valid = lambda word: keep_correct(word) and exclude_absent(word) and move_present(word)

        valid_words = list(filter(is_valid, valid_words))

    return valid_words

if __name__ == '__main__':
    with open('data/words.txt', 'r') as f:
        words = [i.strip('\n').strip('"') for i in f.read().split(',')]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.nytimes.com/games/wordle/index.html')
        print("Click play")

        time.sleep(5)
        avoid_rules(page)

        guesses = []
        hints = []
        plausible = [word for word in words]

        while not all_correct(page, hints) and len(guesses) < 6:
            random.shuffle(plausible)
            guesses.append(plausible[0])
            guess_word(page, guesses[-1])
            time.sleep(2.1)
            hints.append(get_hints(page, len(guesses)))
            plausible = prune(words, hints)