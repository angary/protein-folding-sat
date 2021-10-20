# Hannah Brown, 10/20/19
# Generates a given number of length n binary sequence files, each with a given
# percentage of ones.

# Modified by Gary Sun, 20/11/21

import random
import sys

def main(argv):
    length = int(argv[1])
    n = int(argv[2])
    prob = float(argv[3])
    file_path = "input/" if len(argv) < 5 else argv[4]
    file_name_base = file_path + "/" + argv[5] if len(argv) == 6 else file_path + "/gen_length_" + str(length)
    strings = []

    while len(strings) < n:

        # Generate random sequence
        next_str = "".join(["1" if random.uniform(0, 1/prob) <= 1 else "0" for _ in range(length)])
        print(next_str)

        # If this has not been added
        if next_str not in strings:
            strings.append(next_str)
            file_name = file_name_base + "_" + str(len(strings))

            with open(file_name, "w+") as f:
                print(strings[len(strings) - 1])
                print(strings[len(strings) - 1], file=f)


if __name__ == "__main__":
    main(sys.argv)
