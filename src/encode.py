"""Take in a string of 1s and 0s and convert it into a bule & DIMACS encoding"""

from __future__ import annotations

import argparse
import os
import subprocess
import time
from typing import Callable

from src.config import TEST_REPEATS
from src.search_policies import *

RESULTS_DIR = "results/"
CSV_HEADER = "length,encode_time,total_time,sat_time,vars,cls"


def main() -> None:
    """Extract arguments and determine whether to perform an encoding or solve"""
    args = parse_args()
    input_file = args.input_file
    goal_contacts = args.goal_contacts
    dim = args.dimension
    ver = args.version
    use_cached = args.use_cached
    policy = eval(args.policy)
    solver = args.solver
    if args.solve and args.track:
        print("Attempting to solve and time\n")
        global RESULTS_DIR
        RESULTS_DIR = os.path.join(RESULTS_DIR, args.results_dir)
        timed_solve(input_file, dim, ver, policy, use_cached, solver)
    elif args.solve:
        print("Attempting to solve\n")
        print(f"Max contacts: {policy(input_file, dim, ver, use_cached, solver)}")
    else:
        print("Attempting to encode\n")
        file_path = encode(input_file, goal_contacts, dim, ver, False, use_cached)
        print(f"Encoding bul    : {file_path.replace('.cnf', '.bul')}")
        print(f"Encoding dimacs : {file_path}")


def timed_solve(
    seq_file: str,
    dim: int,
    ver: int,
    policy: Callable,
    use_cached: bool,
    solver: str
) -> None:
    """Time how long it takes to solve a contact and write it into a file"""
    length = len(get_sequence(seq_file))
    filename = seq_file.split("/")[-1]
    search_initials = "".join([x[0] for x in policy.__name__.split("_")])
    result_name = f"{filename}_{dim}d_v{ver}_{solver[0]}s_{search_initials}"
    results_file = f"{os.path.join(RESULTS_DIR, result_name)}.csv"

    with open(results_file, "w+") as f:
        f.write(f"{CSV_HEADER}\n")
    for _ in range(TEST_REPEATS):
        r = policy(seq_file, dim, ver, use_cached, solver)
        v, c = get_num_vars_and_clauses(filename, dim, ver, r['max_contacts'])
        print(results_file)
        results = [length, r["encode_time"], r["solve_time"], r["sat_solve_time"], v, c]
        string = ",".join(list(map(str, results)))
        with open(results_file, "a") as f:
            f.write(f"{string}\n")


def solve_sat(seq_file: str, goal: int, dim: int, ver: int, use_cached: bool, solver) -> tuple[float, float]:
    """Encode and solve input, then return tuple (encode duration, solve duration)"""
    start = time.time()
    file_path = encode(seq_file, goal, dim, ver, False, use_cached)
    print(f"{file_path = }")
    encode_duration = time.time() - start

    start = time.time()
    output = str(subprocess.run([solver, file_path], capture_output=True).stdout)
    solve_duration = time.time() - start

    if "UNSAT" in output:
        print("UNSAT")
        return (encode_duration, -solve_duration)
    elif "SAT" in output:
        print("SAT")
        return (encode_duration, solve_duration)
    print(f"There was a bug in solving with bule. Output: {output}")
    return (0, 0)


def encode(
    seq_file: str,
    goal: int,
    dim: int,
    ver: int,
    tracked: bool,
    use_cached: bool
) -> str:
    """Generate bule encoding and write it to a file in the models folder that path"""
    filename = seq_file.split("/")[-1]
    seq = get_sequence(seq_file)
    w = get_grid_diameter(dim, len(seq))
    in_file = f"models/bul/{filename}_d{dim}_v{ver}_{goal}c.bul"

    # Number of contacts = adjacent "1"s minus offset
    with open(in_file, "w+") as f:
        f.write(f"% {seq}\n\n")
        f.writelines([f"#ground sequence[{i}, {c}].\n" for i, c in enumerate(seq)] + ["\n"])
        f.writelines([
            f"#ground width[{w}].\n",
            f"#ground goal[{(get_adjacent_ones(seq) + goal)}].\n",
            f"#ground dim[0..{dim - 1}].\n"
        ])
    
    # Generate encoding
    bule_files = f"{get_encoding_file(dim, ver)} bule/cc_a.bul"
    output = f"models/cnf/{filename}_{dim}d_v{ver}_{goal}c.cnf"
    start = time.time()
    if not use_cached or not os.path.isfile(output):
        subprocess.run(f"bule2 --output dimacs {bule_files} {in_file} > {output}", shell=True)
        encode_time = time.time() - start
    else:
        encode_time = 0

    if tracked:
        result_name = f"{filename}_{dim}d_v{ver}_NAs_NAp"
        with open(f"{os.path.join(RESULTS_DIR, result_name)}.csv", "w+") as f:
            vars, clauses = get_num_vars_and_clauses(filename, dim, ver, goal)
            f.write(f"{CSV_HEADER}\n")
            f.write(f"{len(seq)},{encode_time},0,0,0,{vars},{clauses}")
    return output


def get_encoding_file(dim: int, v: int) -> str:
    return f"bule/constraints_v{v}.bul" if v > 0 else f"bule/constraints_{dim}d_v0.bul"


def get_num_vars_and_clauses(filename: str, dim: int, v: int, goal: int) -> tuple[int, int]:
    with open(f"models/cnf/{filename}_{dim}d_v{v}_{goal}c.cnf") as f:
        return tuple(map(int, f.readline().split()[-2:]))


def get_sequence(seq_file: str) -> str:
    with open(seq_file, "r") as f:
        return f.readline().removesuffix("\n")


def get_adjacent_ones(s: str) -> int:
    return [s[i] == s[i+1] == "1" for i in range(len(s)-1)].count(True)


def get_grid_diameter(dim: int, n: int) -> int:
    if dim == 2:
        if n >= 12:
            return 1 + n // 4
        return n
    if n >= 20:
        return 2 + n // 8
    return 2 + n // 4


def get_max_contacts(s: str, dim: int) -> int:
    n = len(s)
    max_adj = 2 if dim == 2 else 4
    total = 0
    for i in range(n - 3):
        if s[i] == "1":
            total += min(max_adj, s[i+3:n:2].count("1"))
    return total


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        help="the path to the input file containing a string of 1s and 0s"
    )
    parser.add_argument(
        "-d", "--dimension",
        nargs="?", type=int, default=2, choices={2, 3},
        help="the dimension of the embedding grid, default value: 2"
    )
    parser.add_argument(
        "-g", "--goal-contacts",
        nargs="?", type=int, default=1,
        help="the goal number of (H-H) contacts, default value: 1"
    )
    parser.add_argument(
        "-p", "--policy",
        nargs="?", type=str, default="double_linear_policy",
        choices={"binary_search_policy", "double_linear_policy", "double_binary_policy"},
        help="the search policy used to find the maximum number of contacts"
    )
    parser.add_argument(
        "-r", "--results-dir",
        nargs="?", type=str, default="encoding",
        choices={"encoding", "policy", "solver"},
        help="the subfolder within the results directory to store the results"
    )
    parser.add_argument(
        "-s", "--solve",
        action="store_true",
        help="solve for the maximum number of contacts"
    )
    parser.add_argument(
        "--solver",
        nargs="?", type=str, default="kissat",
        choices={"glucose", "kissat", "minisat"},
        help="the SAT solver used"
    )
    parser.add_argument(
        "-t", "--track",
        action="store_true",
        help="record details such as time, clauses, etc when a solving an encoding"
    )
    parser.add_argument(
        "-v", "--version",
        nargs="?", type=int, default=2,
        help="Select which encoding version to use"
    )
    parser.add_argument(
        "-u", "--use-cached",
        action="store_true",
        help="use the already generated dimacs file when testing multiple times"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
