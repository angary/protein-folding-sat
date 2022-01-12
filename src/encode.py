"""Take in a string of 1s and 0s and convert it into a bul encoding"""

import argparse
import os
import subprocess
import time
from typing import Callable

from src.config import TEST_REPEATS

RESULTS_DIR = "results/encoding/"
CSV_HEADER = "length,encode_time,total_time,sat_time,vars,cls,solver,policy"


def main() -> None:
    """Extract arguments and determine whether to perform an encoding or solve"""
    args = parse_args()
    input_file = args.input_file
    goal_contacts = args.goal_contacts
    dim = args.dimension
    ver = args.version
    use_cached = args.use_cached
    search = eval(args.policy)
    if args.solve and args.track:
        print("Attempting to solve and time\n")
        timed_solve(input_file, dim, ver, search, use_cached)
    elif args.solve:
        print("Attempting to solve\n")
        print(f"Max contacts: {search(input_file, dim, ver, use_cached)}")
    else:
        print("Attempting to encode\n")
        file_path = encode(input_file, goal_contacts, dim, ver, False, use_cached)
        print(f"Encoding bul    : {file_path.replace('.cnf', '.bul')}")
        print(f"Encoding dimacs : {file_path}")


def solve_binary(seq_file: str, dim: int, ver: int, use_cached: bool) -> dict[str, float]:
    """Binary search for max contacts"""
    total_encode_time, total_solve_time, sat_solve_time = 0.0, 0.0, 0.0
    lo, hi = 0, get_max_contacts(get_sequence(seq_file), dim)
    print(f"Start binary search to max contacts from {hi = }")
    while lo <= hi:
        curr = (hi + lo) // 2
        print(f"Solving {curr}:", end=" ", flush=True)
        encode_time, solve_time = solve_sat(seq_file, curr, dim, ver, use_cached)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        if solve_time > 0:
            lo = curr + 1
            sat_solve_time += solve_time
        else:
            curr -= 1
            hi = curr
    print()
    return {
        "max_contacts": curr,
        "encode_time": total_encode_time,
        "solve_time": total_solve_time,
        "sat_solve_time": sat_solve_time
    }


def solve_double_linear(seq_file: str, dim: int, ver: int, use_cached: bool) -> dict[str, float]:
    """Double till UNSAT, then linear search for max contacts"""
    # Double goal_contacts until it is unsolvable
    curr = 1
    max_contacts = get_max_contacts(get_sequence(seq_file), dim)
    total_encode_time, total_solve_time, sat_solve_time = 0.0, 0.0, 0.0
    print(f"Start doubling until {max_contacts = }")
    while curr <= max_contacts:
        print(f"Solving {curr}: ", end="", flush=True)
        encode_time, solve_time = solve_sat(seq_file, curr, dim, ver, use_cached)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        if solve_time <= 0:
            break
        sat_solve_time += solve_time
        curr *= 2
    print(f"Failed to solve at {curr}\n")

    # Linear search to the maximum possible value
    curr = curr // 2 - 1
    print("Start linear search to max contacts")
    while curr < max_contacts:
        curr += 1
        print(f"Solving {curr}:", end=" ", flush=True)
        encode_time, solve_time = solve_sat(seq_file, curr, dim, ver, use_cached)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        if solve_time <= 0:
            curr -= 1
            break
        sat_solve_time += solve_time
    print()
    return {
        "max_contacts": curr,
        "encode_time": total_encode_time,
        "solve_time": total_solve_time,
        "sat_solve_time": sat_solve_time
    }

def solve_double_binary(seq_file: str, dim: int, ver: int, use_cached: bool) -> dict[str, float]:
    """
    Start the contacts at 1 doubling until unsolvable. Then binary search for the max solvable
    """
    # Double goal_contacts until it is unsolvable
    curr = 1
    max_contacts = get_max_contacts(get_sequence(seq_file), dim)
    total_encode_time, total_solve_time, sat_solve_time = 0.0, 0.0, 0.0
    print(f"Start doubling until {max_contacts = }")
    while curr <= max_contacts:
        print(f"Solving {curr}: ", end="", flush=True)
        encode_time, solve_time = solve_sat(seq_file, curr, dim, ver, use_cached)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        if solve_time <= 0:
            break
        sat_solve_time += solve_time
        curr *= 2
    print(f"Failed to solve at {curr}\n")

    # Binary search to the maximum possible value
    lo, hi = curr // 2 + 1, curr - 1
    print("Start binary search to max contacts")
    while lo <= hi:
        curr = (hi + lo) // 2
        print(f"Solving {curr}:", end=" ")
        encode_time, solve_time = solve_sat(seq_file, curr, dim, ver, use_cached)
        total_encode_time += abs(encode_time)
        total_solve_time += abs(solve_time)
        if solve_time > 0:
            lo = curr + 1
            sat_solve_time += solve_time
        else:
            curr -= 1
            hi = curr
    print()
    return {
        "max_contacts": curr,
        "encode_time": total_encode_time,
        "solve_time": total_solve_time,
        "sat_solve_time": sat_solve_time
    }

def timed_solve(
    seq_file: str,
    dim: int,
    ver: int,
    search: Callable = solve_double_linear,
    use_cached: bool = False,
    solver: str = "kissat",
) -> None:
    """Time how long it takes to solve a contact and write it into a file"""
    length = len(get_sequence(seq_file))
    filename = seq_file.split("/")[-1]
    results_file = f"{RESULTS_DIR}{filename}_{dim}d_v{ver}.csv"

    with open(results_file, "w+") as f:
        f.write(f"{CSV_HEADER}\n")
    for _ in range(TEST_REPEATS):
        r = search(seq_file, dim, ver, use_cached)
        v, c = get_num_vars_and_clauses(filename, dim, ver, r['max_contacts'])
        print(results_file)
        with open(results_file, "a") as f:
            string = ",".join(list(map(str, [
                length,
                r["encode_time"],
                r["solve_time"],
                r["sat_solve_time"],
                v,
                c,
                solver,
                search.__name__
            ])))
            f.write(f"{string}\n")


def solve_sat(seq_file: str, goal: int, dim: int, ver: int, use_cached: bool) -> tuple[float, float]:
    """Encode and solve input, then return tuple (encode duration, solve duration)"""
    start = time.time()
    file_path = encode(seq_file, goal, dim, ver, False, use_cached)
    print(f"{file_path = }")
    encode_duration = time.time() - start

    command = f"kissat {file_path} -q"

    start = time.time()
    output = str(subprocess.run(command.split(), capture_output=True).stdout)
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
    file_name = seq_file.split("/")[-1]
    seq = get_sequence(seq_file)
    w = get_grid_diameter(dim, len(seq))
    in_file = f"models/bul/{file_name}_d{dim}_v{ver}_{goal}c.bul"

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
    output = f"models/cnf/{file_name}_{dim}d_v{ver}_{goal}c.cnf"
    start = time.time()
    if not use_cached or not os.path.isfile(output):
        subprocess.run(f"bule2 --output dimacs {bule_files} {in_file} > {output}", shell=True)
        encode_time = time.time() - start
    else:
        encode_time = 0

    if tracked:
        with open(f"{RESULTS_DIR}{file_name}_{dim}d_v{ver}.csv", "w+") as f:
            vars, clauses = get_num_vars_and_clauses(file_name, dim, ver, goal)
            f.write(f"{CSV_HEADER}\n")
            f.write(f"{len(seq)},{encode_time},0,0,0,{vars},{clauses},NA,NA")
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
        nargs="?", type=str, default="solve_double_linear",
        choices={"solve_binary", "solve_double_linear", "solve_double_binary"},
        help="the search policy used to find the maximum number of contacts"
    )
    parser.add_argument(
        "-s", "--solve",
        action="store_true",
        help="solve for the maximum number of contacts"
    )
    parser.add_argument(
        "-t", "--track",
        action="store_true",
        help="record details such as time, clauses, etc when a solving an encoding"
    )
    parser.add_argument(
        "-v", "--version",
        nargs="?", type=int, default=1,
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
