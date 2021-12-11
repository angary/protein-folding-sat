"""
Check that when solving using the following encodings, they produce the
same number of max contacts.
"""
import os

from src.encode import get_num_vars_and_clauses, encode, solve
from src.run_tests import get_sequences

INPUT_DIR = "input"
OUTPUT = "validate.log"
COMPARE: list[tuple[int, int]] = [
    (2, 1),
    (2, 2)
]

def main():
    for sequence in get_sequences(INPUT_DIR, "all", max_len=20):
        filename = os.path.join(INPUT_DIR, sequence["filename"])
        results = []
        for dim, version in COMPARE:
            output = encode(filename, 1, dim, version)
            print(output)
            v, c = get_num_vars_and_clauses(sequence["filename"], version)
            r = solve(filename, dim, version)
            results += [[v, c, r["max_contacts"], r["duration"]]]
        result_str = "\n".join(list(map(str,results)))
        with open(OUTPUT, "a") as f:
            f.write(f"{filename}\nVars, Clauses, Max Contacts, Duration\n")
            f.write(f"{result_str}\n")
            f.write(f"Same contacts : {results[0][2] == results[1][2]}\n")
            f.write(f"Leq variables : {results[0][0] >= results[1][0]}\n")
            f.write(f"Leq clauses   : {results[0][1] >= results[1][1]}\n")
            f.write(f"Less time     : {results[0][3] >= results[1][3]}\n\n")

if __name__ == "__main__":
    main()
