# Hannah Brown, 10/20/19
# Generates a given number of length n binary sequence files, each with a given
# percentage of ones.

# Modified by Gary Sun, 20/9/21

import os
import random

SEED = 1
PROB = 2/3
FILE_PATH = "input/"
N = 10

def main():
    random.seed(SEED)
    for i in range(6, 50):
        gen_sequences(i)


def gen_sequences(length: int):
    file_name_base = f"{os.path.join(FILE_PATH, 'length')}-{length}"
    strings: list[str] = []

    while len(strings) < N:

        # Generate random sequence
        next_str = "".join(["1" if random.uniform(0, 1/PROB) <= 1 else "0" for _ in range(length)])

        # If this has not been added
        if next_str not in strings:
            strings.append(next_str)
            file_name = f"{file_name_base}-{len(strings)}"

            with open(file_name, "w+") as f:
                print(strings[len(strings) - 1])
                print(strings[len(strings) - 1], file=f)


if __name__ == "__main__":
    main()
