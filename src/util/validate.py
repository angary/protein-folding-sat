"""
Check that when solving using the following encodings, they produce the
same number of max contacts.
"""
import os
from typing import Callable

from src.encode import encode, get_num_vars_and_clauses, solve_binary, \
    solve_binary_binary, solve_binary_linear
from src.run_tests import get_sequences

MIN_LEN = 0
MAX_LEN = 23
INPUT_DIR = "input"
OUTPUT = "validate.log"

# List containing tuple of [dimension, version] of the encodings to compare
ENCODINGS: list[tuple[int, int]] = [
    (2, 1),
    # (2, 2)
]

# List containing functions of the different search methods to compare
FUNCTIONS: list[Callable] = [
    solve_binary,
    solve_binary_binary,
    solve_binary_linear
]

# Flag to choose if we compare encodings or methods of search
COMPARE_ENCODINGS = False

def main():
    vs = []
    cs = []
    ts = []

    times = {func.__name__: 0 for func in FUNCTIONS}

    with open(OUTPUT, "w+") as f:
        pass

    for sequence in get_sequences(INPUT_DIR, "all", min_len=MIN_LEN, max_len=MAX_LEN):
        filename = os.path.join(INPUT_DIR, sequence["filename"])
        results = []

        # Compare different encodings
        if COMPARE_ENCODINGS:
            for dim, version in ENCODINGS:
                output = encode(filename, 1, dim, version)
                print(output)
                v, c = get_num_vars_and_clauses(sequence["filename"], version)
                r = solve_binary_binary(filename, dim, version)
                results.append([version, v, c, r["duration"], r["max_contacts"]])
            
            variable_diff = (results[1][0] - results[0][0]) / min(results[0][0], results[1][0])
            clause_diff = (results[1][1] - results[0][1]) / min(results[0][1], results[1][1])
            if min(results[1][2], results[0][2]) != 0:
                time_diff = (results[1][2] - results[0][2]) / min(results[0][2], results[1][2]) 
            else:
                time_diff = 0

            vs.append(variable_diff)
            cs.append(clause_diff)
            ts.append(time_diff)

            result_str = "\n".join(list(map(str, results)))
            with open(OUTPUT, "a") as f:
                f.write(f"{filename}\nVersion, Vars, Clauses, Duration, Contacts\n")
                f.write(f"{result_str}\n")
                f.write(f"Same contacts : {results[0][3] == results[1][3]}\n")
                f.write(f"Leq variables : {variable_diff <= 0} {variable_diff}\n")
                f.write(f"Leq clauses   : {clause_diff <= 0} {clause_diff}\n")
                f.write(f"Less time     : {time_diff <= 0} {time_diff}\n\n")
        else:
            for func in FUNCTIONS:
                r = func(filename, 2, 1)
                results.append([func.__name__, r["duration"], r["max_contacts"]])
                times[func.__name__] += r["duration"]
            with open(OUTPUT, "a") as f:
                f.write(f"{filename}\nFunction, Duration, contacts\n")
                f.write("\n".join(list(map(str, results))) + "\n")
                f.write(f"Same num of contacts: {len(set(list(zip(*results))[2])) == 1}\n\n")
    
    if COMPARE_ENCODINGS:
        with open(OUTPUT, "a") as f:
            f.write("\n\n")
            f.write(f"Avg variables -> {sum(vs) / len(vs)}\n")
            f.write(f"Avg clauses -> {sum(cs) / len(cs)}\n")
            f.write(f"Avg time -> {sum(ts) / len(ts)}\n")
    else:
        with open(OUTPUT, "a") as f:
            f.write("\n\n")
            for func_name, total_duration in times.items():
                f.write(f"{func_name}: {total_duration}\n")


if __name__ == "__main__":
    main()
