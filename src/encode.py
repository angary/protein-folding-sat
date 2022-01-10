"""Take in a string of 1s and 0s and convert it into a bul encoding"""

import argparse
import os
import subprocess
import time
from typing import Callable

from src.config import TEST_REPEATS

RESULTS_DIR = "results/encoding/"

def main() -> None:
    """Extract arguments and determine whether to perform an encoding or solve"""
    args = parse_args()
    input_file = args.input_file
    goal_contacts = args.goal_contacts
    dimension = args.dimension
    version = args.version
    use_cached = args.use_cached
    if args.solve and args.track:
        print("Attempting to solve and time\n")
        timed_solve(input_file, dimension, version, solve_binary_linear, use_cached)
    elif args.solve:
        print("Attempting to solve\n")
        print(f"Max contacts: {solve_binary_linear(input_file, dimension, version, use_cached)}")
    else:
        print("Attempting to encode\n")
        file_path = encode(input_file, goal_contacts, dimension, version, use_cached)
        print(f"Encoding bul    : {file_path.replace('.cnf', '.bul')}")
        print(f"Encoding kissat : {file_path}")


def solve_binary(input_file: str, dim: int, version: int, use_cached: bool = False) -> dict[str, float]:
    """Binary search for max contacts"""
    total_duration, lo, hi = 0.0, 0
    lo, hi = 0, get_max_contacts(get_sequence(input_file), dim)
    goal_contacts = (hi + lo) // 2
    print(f"Start binary search to max contacts from {hi = }")
    while lo <= hi:
        goal_contacts = (hi + lo) // 2
        print(f"Solving {goal_contacts}:", end=" ")
        duration = solve_sat(input_file, goal_contacts, dim, version, use_cached)
        total_duration += abs(duration)
        if duration > 0:
            lo = goal_contacts + 1
        else:
            hi = goal_contacts - 1
            goal_contacts -= 1
    print()
    return { "max_contacts": goal_contacts, "duration": total_duration }


def solve_binary_linear(input_file: str, dim: int, version: int, use_cached: bool = False) -> dict[str, float]:
    """Double till UNSAT, then linear search for max contacts"""
    # Double goal_contacts until it is unsolvable
    goal_contacts = 1
    max_contacts = get_max_contacts(get_sequence(input_file), dim)
    total_duration = 0.0
    print(f"Start doubling until {max_contacts = }")
    while goal_contacts <= max_contacts:
        print(f"Solving {goal_contacts}: ", end="", flush=True)
        duration = solve_sat(input_file, goal_contacts, dim, version, use_cached)
        total_duration += abs(duration)
        if duration <= 0:
            break
        goal_contacts *= 2
    print(f"Failed to solve at {goal_contacts}\n")

    # Linear search to the maximum possible value
    goal_contacts = goal_contacts // 2 - 1
    print("Start linear search to max contacts")
    while goal_contacts < max_contacts:
        goal_contacts += 1
        print(f"Solving {goal_contacts}:", end=" ")
        duration = solve_sat(input_file, goal_contacts, dim, version, use_cached)
        total_duration += abs(duration)
        if duration <= 0:
            goal_contacts -= 1
            break
    print()
    return { "max_contacts": goal_contacts, "duration": total_duration }


def solve_binary_binary(input_file: str, dim: int, version: int, use_cached: bool = False) -> dict[str, float]:
    """
    Start the goal contacts at 1 and then attempt to solve it, doubling the
    goal contacts until it is unsolvable. Then binary search for the largest
    possible value goal contacts can be whilst solvable and return it.
    """
    # Double goal_contacts until it is unsolvable
    goal_contacts = 1
    max_contacts = get_max_contacts(get_sequence(input_file), dim)
    total_duration = 0.0
    print(f"Start doubling until {max_contacts = }")
    while goal_contacts <= max_contacts:
        print(f"Solving {goal_contacts}: ", end="", flush=True)
        duration = solve_sat(input_file, goal_contacts, dim, version, use_cached)
        total_duration += abs(duration)
        if duration <= 0:
            break
        goal_contacts *= 2
    print(f"Failed to solve at {goal_contacts}\n")

    # Binary search to the maximum possible value
    lo = goal_contacts // 2 + 1
    hi = goal_contacts - 1
    goal_contacts = (hi + lo) // 2
    print("Start binary search to max contacts")
    while lo <= hi:
        goal_contacts = (hi + lo) // 2
        print(f"Solving {goal_contacts}:", end=" ")
        duration = solve_sat(input_file, goal_contacts, dim, version, use_cached)
        total_duration += abs(duration)
        if duration > 0:
            lo = goal_contacts + 1
        else:
            hi = goal_contacts - 1
            goal_contacts -= 1
    print()
    return { "max_contacts": goal_contacts, "duration": total_duration }


def timed_solve(
    input_file: str,
    dim: int,
    version: int,
    search: Callable = solve_binary_linear,
    use_cached: bool = False
) -> None:
    """Time how long it takes to solve a contact and write it into a file"""
    length = len(get_sequence(input_file))
    filename = input_file.split("/")[-1]
    results_file = f"{RESULTS_DIR}{filename}_{dim}d_v{version}.csv"

    with open(results_file, "w+") as f:
        f.write("length,time,contacts,variables,clauses\n")
    for _ in range(TEST_REPEATS):
        r = search(input_file, dim, version, use_cached)
        vars, clauses = get_num_vars_and_clauses(filename, dim, version, r['max_contacts'])
        print(results_file)
        with open(results_file, "a") as f:
            f.write(f"{length},{r['duration']},{r['max_contacts']},{vars},{clauses}\n")


def solve_sat(input_file: str, goal_contacts: int, dim: int, version: int, use_cached: bool = False) -> float:
    """
    Run an encoding of the input file, with the target goal of contacts and
    return the duration for solving if it managed
    """
    file_path = encode(input_file, goal_contacts, dim, version, use_cached=use_cached)
    command = f"kissat {file_path} -q"
    start = time.time()
    output = str(subprocess.run(command.split(), capture_output=True).stdout)
    duration = time.time() - start
    if "UNSAT" in output:
        print("UNSAT")
        return -duration
    elif "SAT" in output:
        print("SAT")
        return duration
    print(f"There was a bug in solving with bule. Output: {output}")
    return 0


def encode(
    seq_file: str,
    goal_contacts: int,
    dim: int,
    version: int,
    tracked: bool = False,
    use_cached: bool = False
) -> str:
    """
    Generate bule encoding for a protein sequence and write it to a file in
    the models folder, returning the path to the file
    """
    file_name = seq_file.split("/")[-1]
    sequence = get_sequence(seq_file)
    base_goal = get_adjacent_ones(sequence)
    w = get_grid_diameter(dim, len(sequence))
    in_file = f"models/bul/{file_name}_d{dim}_v{version}_{goal_contacts}c.bul"

    # Number of contacts = adjacent "1"s minus offset
    with open(in_file, "w+") as f:
        f.write(f"% {sequence}\n\n")
        f.writelines([f"#ground sequence[{i}, {c}].\n" for i, c in enumerate(sequence)] + ["\n"])
        f.writelines([
            f"#ground width[{w}].\n",
            f"#ground goal[{(base_goal + goal_contacts)}].\n",
            f"#ground dim[0 .. {dim - 1}].\n"
        ])
    bule_files = f"{get_encoding_file(dim, version)} bule/cc_a.bul"
    output = f"models/cnf/{file_name}_{dim}d_v{version}_{goal_contacts}c.cnf"
    if not use_cached or not os.path.isfile(output):
        subprocess.run(f"bule2 --output dimacs {bule_files} {in_file} > {output}", shell=True)

    if tracked:
        with open(f"{RESULTS_DIR}{file_name}_{dim}d_{version}.csv", "w+") as f:
            vars, clauses = get_num_vars_and_clauses(file_name, dim, version, goal_contacts)
            f.write("length,time,contacts,variables,clauses\n")
            f.write(f"{len(sequence)},0,0,{vars},{clauses}")
    return output


def get_encoding_file(dim: int, version: int) -> str:
    """Return path to the encoding with the specified dimensiona and version"""
    if version > 0:
        return f"bule/constraints_v{version}.bul"
    return f"bule/constraints_{dim}d_v0.bul"


def get_num_vars_and_clauses(filename: str, dim: int, version: int, goal_contacts: int) -> tuple[int, int]:
    """
    Given the name of the input, return the number of variables and
    clauses in the encoding by reading it from the DIMACS cnf encoded file
    """
    with open(f"models/cnf/{filename}_{dim}d_v{version}_{goal_contacts}c.cnf") as f:
        return tuple(map(int, f.readline().split()[-2:]))


def get_sequence(input_file: str) -> str:
    """Read the input file and return the string sequence of 1s and 0s"""
    with open(input_file, "r") as f:
        return f.readline().removesuffix("\n")


def get_adjacent_ones(s: str) -> int:
    """Return the number of adjacent ones that are in the string"""
    return [s[i] == s[i+1] == "1" for i in range(len(s)-1)].count(True)


def get_grid_diameter(dim: int, n: int) -> int:
    """Return ideal grid diameter, given the dimension and protein length"""
    if dim == 2:
        if n >= 12:
            return 1 + n // 4
        return n
    if n >= 20:
        return 2 + n // 8
    return 2 + n // 4


def get_max_contacts(s: str, dim: int) -> int:
    """Find the maximum number of contacts that the sequence can have"""
    n = len(s)
    max_adj = 2 if dim == 2 else 4
    # The maximum number of potential contacts that the ith "1" can have
    potential_contacts = [max_adj if i == "1" else 0 for i in s ] 
    total = 0
    for i in range(n - 3):
        # Each "1" can only contact at max 4 (in 2d) or 6 (in 3d) other "1"s 
        # that are at least 3 indexes away, and an odd distance away
        if s[i] == "1" and potential_contacts[i] > 0:
            # Max indexes that this index can contact with on the right
            for j in range(i+3, n, 2):
                if potential_contacts[i] == 0:
                    break
                if s[j] == "1":
                    potential_contacts[i] -= 1
                    potential_contacts[j] -= 1
                    total += 1
    return total


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        help="the path to the input file containing a string of 1s and 0s"
    )
    parser.add_argument(
        "-g", "--goal-contacts",
        nargs="?", type=int, default=1,
        help="the goal number of (H-H) contacts, default value: 1"
    )
    parser.add_argument(
        "-d", "--dimension",
        nargs="?", type=int, default=2, choices={2, 3},
        help="the dimension of the embedding grid, default value: 2"
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
