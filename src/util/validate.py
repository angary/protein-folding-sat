"""
Check that when solving using the following encodings, they produce the
same number of max contacts.
"""
from __future__ import annotations
import os

from src.encode import encode, get_num_vars_and_clauses, get_max_contacts
from src.run_tests import get_sequences
from src.search_policies import *

DEFAULT_DIMENSION = 2
DEFAULT_VERSION = 2
DEFAULT_SOLVER = "kissat"

MIN_LEN, MAX_LEN = 10, 25

INPUT_DIR = "input"
OUTPUT = "validate.log"
USE_CACHED = False

# List containing tuple of [dimension, version] of the encodings to compare
ENCODINGS = [(3, 1), (3, 3)]

# List containing functions of the different search methods to compare
FUNCTIONS = [binary_search_policy, linear_search_policy,
             double_binary_policy, double_linear_policy]

COUNT_ENCODINGS = ["cc_a.bul", "counter.bul"]

# Flag to choose if we compare encodings or methods of search
# {"encoding", "policy", "counting"}
COMPARISON = "encoding"

def main():
    with open(OUTPUT, "w+") as f:
        pass
    if COMPARISON == "counting":
        compare_counting()
    elif COMPARISON == "encoding":
        compare_encodings()
    elif COMPARISON == "policy":
        compare_policies()


def compare_encodings():
    vs = []
    cs = []
    ts = []
    for sequence in get_sequences(INPUT_DIR, "all", min_len=MIN_LEN, max_len=MAX_LEN):
        filename = os.path.join(INPUT_DIR, sequence["filename"])
        results = []

        # Compare different encodings
        goal_contacts = 1
        for dim, version in ENCODINGS:
            output = encode(filename, goal_contacts, dim,
                            version, False, USE_CACHED)
            print(output)
            v, c = get_num_vars_and_clauses(
                sequence["filename"], dim, version, goal_contacts)
            r = linear_search_policy(
                filename, dim, version, USE_CACHED, DEFAULT_SOLVER, "counter.bul")
            results.append({
                "ver": version,
                "vars": v,
                "cls": c,
                "encode_time": round(r["encode_time"], 4),
                "solve_time": round(r["solve_time"], 4),
                "sat_time": round(r["sat_solve_time"], 4),
                "contacts": r["max_contacts"]
            })
        if len(ENCODINGS) > 1:
            a, b = results[0:2]
            var_diff = (b["vars"] - a["vars"]) / a["vars"]
            clause_diff = (b["cls"] - a["cls"]) / a["cls"]
            time_diff = (b["solve_time"] - a["solve_time"]) / \
                a["solve_time"] if min(
                b["solve_time"], a["solve_time"]) != 0 else 0

            vs.append(b["vars"] - a["vars"])
            cs.append(b["cls"] - a["cls"])
            ts.append(b["solve_time"] - a["solve_time"])

        result_str = "\n".join(list(map(str, results)))
        mc = get_max_contacts(sequence['seq'], dim)
        with open(OUTPUT, "a") as f:
            f.write(f"{filename = } | Max contacts = {mc}\n")
            f.write(f"{result_str}\n")
            if len(ENCODINGS) > 1:
                f.write(f"Same contacts : {a['contacts'] == b['contacts']}\n")
                f.write(f"Leq variables : {var_diff <= 0} {var_diff}\n")
                f.write(f"Leq clauses   : {clause_diff <= 0} {clause_diff}\n")
                f.write(f"Less time     : {time_diff <= 0} {time_diff}\n")
            f.write("\n")
    if len(ENCODINGS) > 1:
        with open(OUTPUT, "a") as f:
            f.write("\n\n")
            f.write(f"Avg variables -> {sum(vs) / len(vs)}\n")
            f.write(f"Avg clauses -> {sum(cs) / len(cs)}\n")
            f.write(f"Avg time -> {sum(ts) / len(ts)}\n")


def compare_policies():

    times = {func.__name__: 0 for func in FUNCTIONS}

    for sequence in get_sequences(INPUT_DIR, "all", min_len=MIN_LEN, max_len=MAX_LEN):
        filename = os.path.join(INPUT_DIR, sequence["filename"])
        results = []

        # Compare different encodings
        for func in FUNCTIONS:
            r = func(filename, DEFAULT_DIMENSION,
                     DEFAULT_VERSION, USE_CACHED, DEFAULT_SOLVER)
            results.append(
                [func.__name__, r["solve_time"], r["max_contacts"]])
            times[func.__name__] += r["solve_time"]
        a, b = results[0:2]
        time_diff = (b[1] - a[1]) / a[1] if min(b[1], a[1]) != 0 else 0
        mc = get_max_contacts(sequence["seq"], DEFAULT_DIMENSION)
        same_contacts = len(set(list(zip(*results))[2])) == 1
        with open(OUTPUT, "a") as f:
            f.write(f"{filename}\n")
            f.write(f"Function, Duration, Contacts, Max Contacts: {mc}\n")
            f.write("\n".join(list(map(str, results))) + "\n")
            f.write(f"Less time     : {time_diff}")
            f.write(f"Same contacts : {same_contacts}\n\n")
    with open(OUTPUT, "a") as f:
        f.write("\n\n")
        for func_name, total_duration in times.items():
            f.write(f"{func_name}: {total_duration}\n")


def compare_counting():
    for sequence in get_sequences(INPUT_DIR, "all", min_len=MIN_LEN, max_len=MAX_LEN):
        filename = os.path.join(INPUT_DIR, sequence["filename"])
        results = []

        # Compare different counting encodings
        for count_encoding in COUNT_ENCODINGS:
            goal_contacts = 1
            output = encode(filename, goal_contacts, DEFAULT_DIMENSION,
                            DEFAULT_VERSION, False, USE_CACHED, count_encoding)
            print(output)
            v, c = get_num_vars_and_clauses(
                sequence["filename"], DEFAULT_DIMENSION, DEFAULT_VERSION, goal_contacts)
            r = linear_search_policy(
                filename, DEFAULT_DIMENSION, DEFAULT_VERSION, USE_CACHED, DEFAULT_SOLVER, count_encoding)
            results.append({
                "vars": v,
                "cls": c,
                "encode_time": round(r["encode_time"], 4),
                "solve_time": round(r["solve_time"], 4),
                "sat_time": round(r["sat_solve_time"], 4),
                "contacts": r["max_contacts"],
                "encoding": count_encoding
            })
        
        result_str = "\n".join(list(map(str, results)))
        mc = get_max_contacts(sequence['seq'], DEFAULT_DIMENSION)
        if len(COUNT_ENCODINGS) > 1:
            a, b = results[0:2]
            var_diff = (b["vars"] - a["vars"]) / a["vars"]
            clause_diff = (b["cls"] - a["cls"]) / a["cls"]
            time_diff = (b["solve_time"] - a["solve_time"]) / \
                a["solve_time"] if min(
                b["solve_time"], a["solve_time"]) != 0 else 0

        result_str = "\n".join(list(map(str, results)))
        mc = get_max_contacts(sequence['seq'], DEFAULT_DIMENSION)
        with open(OUTPUT, "a") as f:
            f.write(f"{filename = } | Max contacts = {mc}\n")
            f.write(f"{result_str}\n")
            if len(COUNT_ENCODINGS) > 1:
                f.write(f"Same contacts : {a['contacts'] == b['contacts']}\n")
                f.write(f"Leq variables : {var_diff <= 0} {var_diff}\n")
                f.write(f"Leq clauses   : {clause_diff <= 0} {clause_diff}\n")
                f.write(f"Less time     : {time_diff <= 0} {time_diff}\n")
            f.write("\n")
    return


if __name__ == "__main__":
    main()
