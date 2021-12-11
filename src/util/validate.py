"""
Check that when solving using the following encodings, they produce the
same number of max contacts.
"""
import os

from src.encode import get_num_vars_and_clauses, encode, solve
from src.run_tests import get_sequences

MIN_LEN = 0
MAX_LEN = 20
INPUT_DIR = "input"
OUTPUT = "validate.log"
COMPARE: list[tuple[int, int]] = [
    (3, 1),
    (3, 2)
]

def main():
    vs = []
    cs = []
    ts = []

    with open(OUTPUT, "w+") as f:
        pass

    for sequence in get_sequences(INPUT_DIR, "all", min_len=MIN_LEN, max_len=MAX_LEN):
        filename = os.path.join(INPUT_DIR, sequence["filename"])
        results = []
        for dim, version in COMPARE:
            output = encode(filename, 1, dim, version)
            print(output)
            v, c = get_num_vars_and_clauses(sequence["filename"], version)
            r = solve(filename, dim, version)
            results += [[v, c, r["duration"], r["max_contacts"]]]

        variable_diff = (results[1][0] - results[0][0]) / min(results[0][0], results[1][0])
        clause_diff = (results[1][1] - results[0][1]) / min(results[0][1], results[1][1])
        if min(results[1][2], results[0][2]) != 0:
            time_diff = (results[1][2] - results[0][2]) / min(results[0][2], results[1][2]) 
        else:
            time_diff = 0

        vs.append(variable_diff)
        cs.append(clause_diff)
        ts.append(time_diff)

        result_str = "\n".join(list(map(str,results)))
        with open(OUTPUT, "a") as f:
            f.write(f"{filename}\nVars, Clauses, Duration, Contacts\n")
            f.write(f"{result_str}\n")
            f.write(f"Same contacts : {results[0][3] == results[1][3]}\n")
            f.write(f"Leq variables : {variable_diff <= 0} {variable_diff}\n")
            f.write(f"Leq clauses   : {clause_diff <= 0} {clause_diff}\n")
            f.write(f"Less time     : {time_diff <= 0} {time_diff}\n\n")
    
    with open(OUTPUT, "a") as f:
        f.write("\n\n")
        f.write(f"Avg variables -> {sum(vs) / len(vs)}\n")
        f.write(f"Avg clauses -> {sum(cs) / len(cs)}\n")
        f.write(f"Avg time -> {sum(ts) / len(ts)}\n")


if __name__ == "__main__":
    main()
