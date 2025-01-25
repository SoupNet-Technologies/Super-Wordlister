from itertools import product
from password_strength import PasswordStats
import random

path = 'words.txt'
parts = 5

leets = [
    ['a', 'A', '@', '4'],
    ['b', 'B', '8'],
    ['c', 'C'],
    ['d', 'D'],
    ['e', 'E', '3'],
    ['f', 'F'],
    ['g', 'G'],
    ['h', 'H'],
    ['i', 'I', '1', '!'],
    ['j', 'J'],
    ['k', 'K'],
    ['l', 'L', '1', '!'],
    ['m', 'M'],
    ['n', 'N'],
    ['o', 'O', '0', 'x', 'X'],
    ['p', 'P'],
    ['q', 'Q'],
    ['r', 'R'],
    ['s', 'S', '5', '$'],
    ['t', 'T', '7'],
    ['u', 'U', 'v', 'V'],
    ['w', 'W', 'vv', 'VV'],
    ['y', 'Y'],
    ['z', 'Z', '2']
]

leet_map = {}
for leet_list in leets:
    base_char = leet_list[0].lower()
    leet_map[base_char] = set()
    for char in leet_list:
        leet_map[base_char].add(char.lower())
        leet_map[base_char].add(char.upper())
for key in leet_map:
    leet_map[key] = list(leet_map[key])

fixes = [
    '!',
    '?',
    ''
]

def load_file(path):
    try:
        with open(path) as f:
            wrds = f.read().splitlines()
        return wrds
    except FileNotFoundError:
        print(f"Error: File {path} not found.")
        return []

def outfile(wrds, output_dir):
    chunk = round(len(wrds) / parts)
    for part in range(parts):
        try:
            with open(f'{output_dir}/out{part+1}.txt', 'w') as f:
                for v in wrds[chunk*part:chunk*(part+1)]:
                    f.write(f'{v}\n')
        except Exception as e:
            print(f"Error creating output file: {e}")

def get_leets(wrds, leet_map):
    new_wrds = set(wrds)

    for word in wrds:
        char_options = []
        for ch in word: # chars in word
            if ch.lower() in leet_map:
                substitutions = leet_map[ch.lower()]
                if ch.isupper():
                    substitutions = [s.upper() if s.isalpha() else s for s in substitutions]
                char_options.append(substitutions)
            else:
                char_options.append([ch])

        # Generate all combinations
        for combo in product(*char_options):
            new_word = ''.join(combo)
            new_wrds.add(new_word)

    return new_wrds

def get_mux(wrds):
    wrds_list = list(wrds)
    new_wrds = set(wrds)

    for i in range(len(wrds_list)):
        for j in range(len(wrds_list)):
            mux = wrds_list[i] + wrds_list[j]
            new_wrds.add(mux)
    return new_wrds

def get_fix(wrds, pos, fixes):
    new_wrds = set()
    fixes_to_use = fixes.copy()
    if pos == 'pre':
        fixes_to_use.append('00000')
        for fix in fixes_to_use:
            for word in wrds:
                new_word = fix + word
                new_wrds.add(new_word)
    else:
        for fix in fixes_to_use:
            for word in wrds:
                new_word = word + fix
                new_wrds.add(new_word)
    return new_wrds

def culler(wrds, min_len=8, max_len=30, score_range=[0.45, 0.75]):
    new_wrds = []
    for k, word in enumerate(wrds):
        if min_len <= len(word):
            pwscore = PasswordStats(word)
            if pwscore.strength() >= score_range[0] and pwscore.strength() <= score_range[1]:
                new_wrds.append(word)
    return new_wrds

def get_reversed(wrds):
    return {word[::-1] for word in wrds}

def get_shuffled(wrds):
    shuffled_words = set()
    for word in wrds:
        shuffled_word = ''.join(random.sample(word, len(word)))
        shuffled_words.add(shuffled_word)
    return shuffled_words

def get_inserted_random(wrds, chars_to_insert):
    new_wrds = set()
    for word in wrds:
        for i in range(len(word) + 1):
            for _ in range(3):  # Insert 1 to 3 random characters
                char_to_insert = random.choice(chars_to_insert)
                new_word = word[:i] + char_to_insert + word[i:]
                new_wrds.add(new_word)
    return new_wrds

if __name__ == "__main__":
    path = input("Enter the path to the words file: ")  # User input for file path
    output_dir = "out"  # Consider making this user input
    parts = 5  # Consider making this user input

    file = load_file(path)
    if not file:
        print("No words loaded. Exiting.")
        exit(1)  # Exit if no words are loaded

    print('File loaded')

    gotleets = get_leets(file, leet_map)
    print(f'Got {len(gotleets)} words after leet substitutions')

    gotmux = get_mux(gotleets)
    print(f'Got {len(gotmux)} words after concatenation (mux)')

    gotprefix = get_fix(gotmux, 'pre', fixes)
    print(f'Got {len(gotprefix)} words after adding prefixes')

    gotsuffix = get_fix(gotmux, 'suf', fixes)
    print(f'Got {len(gotsuffix)} words after adding suffixes')

    all_wrds = gotmux.union(gotprefix).union(gotsuffix)

    # New functionalities
    reversed_words = get_reversed(all_wrds)
    shuffled_words = get_shuffled(all_wrds)
    random_inserted_words = get_inserted_random(all_wrds, "xyz")  # Example characters to insert

    # Combine all new words
    all_wrds = all_wrds.union(reversed_words).union(shuffled_words).union(random_inserted_words)

    print(f'Total unique words after permutations: {len(all_wrds)}')

    culled = culler(all_wrds)
    print(f'Wrote {len(culled)} lines after culling')

    outfile(culled, output_dir)