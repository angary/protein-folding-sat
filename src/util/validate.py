"""
Check that when solving using the following encodings, they produce the
same number of max contacts.
"""
import os
from typing import Callable

from src.encode import encode, get_num_vars_and_clauses, binary_search_policy, \
    double_binary_policy, double_linear_policy, get_max_contacts
from src.run_tests import get_sequences

MIN_LEN = 0
MAX_LEN = 20
INPUT_DIR = "input"
OUTPUT = "validate.log"
USE_CACHED = True
SOLVER = "kissat"

# List containing tuple of [dimension, version] of the encodings to compare
ENCODINGS: list[tuple[int, int]] = [(2, 0), (2, 2)]

# List containing functions of the different search methods to compare
FUNCTIONS: list[Callable] = [binary_search_policy, double_binary_policy, double_linear_policy]

# Flag to choose if we compare encodings or methods of search
COMPARE_ENCODINGS = True


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
        goal_contacts = 1
        if COMPARE_ENCODINGS:
            for dim, version in ENCODINGS:
                output = encode(filename, goal_contacts, dim, version, False, USE_CACHED)
                print(output)
                v, c = get_num_vars_and_clauses(sequence["filename"], dim, version, goal_contacts)
                r = double_linear_policy(filename, dim, version, USE_CACHED, SOLVER)
                results.append({
                    "ver": version,
                    "vars": v,
                    "cls": c,
                    "encode_time": round(r["encode_time"], 4),
                    "solve_time": round(r["solve_time"], 4),
                    "sat_time": round(r["sat_solve_time"], 4),
                    "contacts": r["max_contacts"]
                })
            a, b = results[0:2]
            variable_diff = (b["vars"] - a["vars"]) / a["vars"]
            clause_diff = (b["cls"] - a["cls"]) / a["cls"]
            time_diff = (b["solve_time"] - a["solve_time"]) / a["solve_time"] if min(b["solve_time"], a["solve_time"]) != 0 else 0

            vs.append(b["vars"] - a["vars"])
            cs.append(b["cls"] - a["cls"])
            ts.append(b["solve_time"] - a["solve_time"])

            result_str = "\n".join(list(map(str, results)))
            with open(OUTPUT, "a") as f:
                f.write(f"{filename = } | Max contacts = {get_max_contacts(sequence['seq'], dim)}\n")
                f.write(f"{result_str}\n")
                f.write(f"Same contacts : {a['contacts'] == b['contacts']}\n")
                f.write(f"Leq variables : {variable_diff <= 0} {variable_diff}\n")
                f.write(f"Leq clauses   : {clause_diff <= 0} {clause_diff}\n")
                f.write(f"Less time     : {time_diff <= 0} {time_diff}\n\n")
        else:
            DIMENSION = 2
            VERSION = 2
            for func in FUNCTIONS:
                r = func(filename, DIMENSION, VERSION, USE_CACHED, SOLVER)
                results.append([func.__name__, r["solve_time"], r["max_contacts"]])
                times[func.__name__] += r["solve_time"]
            a, b = results[0:2]
            time_diff = (b[1] - a[1]) / a[1] if min(b[1], a[1]) != 0 else 0
            with open(OUTPUT, "a") as f:
                f.write(f"{filename}\nFunction, Duration, Contacts, Max Contacts: {get_max_contacts(sequence['seq'], DIMENSION)}\n")
                f.write("\n".join(list(map(str, results))) + "\n")
                # f.write(f"Less time     : {time_diff}")
                f.write(f"Same contacts : {len(set(list(zip(*results))[2])) == 1}\n\n")
    
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
