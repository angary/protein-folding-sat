"""Take in a string of 1s and 0s and convert it into a bul encoding"""

import argparse
import subprocess
import time

TEST_REPEATS = 1


def main() -> None:
    """
    Extract arguments and determine whether to perform an encoding or solve
    """
    args = parse_args()
    input_file = args.input_file
    goal_contacts = args.contacts
    dimension = args.dimension
    new = args.new

    if args.solve and args.track:
        print("Attempting to solve and time\n")
        timed_solve(input_file, dimension, new)
    elif args.solve:
        print("Attempting to solve\n")
        print(f"Max contacts: {solve(input_file, dimension, new)}")
    else:
        print("Attempting to encode\n")
        file_path = encode(input_file, goal_contacts, dimension, new, args.track)
        print(f"Encoding bul    : {file_path.replace('cnf', 'bul')}")
        print(f"Encoding kissat : {file_path}")


def timed_solve(input_file: str, dimension: int, new: bool) -> None:
    """
    Time how long it takes to solve a contact and write it into a file
    """
    length = len(get_sequence(input_file))
    filename = input_file.split("/")[-1]
    encoding_type = "new" if new else "old"
    results_file = f"results/{filename}_{dimension}d_{encoding_type}.csv"

    with open(results_file, "w+") as f:
        f.write("length,time,contacts,variables,clauses\n")
    for _ in range(TEST_REPEATS):
        r = solve(input_file, dimension, new)
        vars, clauses = get_num_vars_and_clauses(filename, new)
        print(results_file)
        with open(results_file, "a") as f:
            f.write(f"{length},{r['duration']},{r['max_contacts']},{vars},{clauses}\n")


def solve(input_file: str, dimension: int, new: bool) -> dict[str, float]:
    """
    Start the goal contacts at 1 and then attempt to solve it, doubling the
    goal contacts until it is unsolvable. Then binary search for the largest
    possible value goal contacts can be whilst solvable and return it.
    """
    # Double goal_contacts until it is unsolvable or it is larger than the
    # maximum number of contacts that it can generate
    goal_contacts = 1
    max_contacts = get_max_contacts(get_sequence(input_file))
    total_duration = 0.0
    print(f"Start doubling until {max_contacts = }")
    while goal_contacts <= max_contacts:
        print(f"Solving {goal_contacts}: ", end="", flush=True)
        duration = solve_sat(input_file, goal_contacts, dimension, new)
        total_duration += abs(duration)
        if 0 >= duration:
            break
        goal_contacts *= 2
    print(f"Failed to solve at {goal_contacts}\n")

    # Binary search to the maximum possible value that the 
    lo = goal_contacts // 2 + 1
    hi = goal_contacts - 1
    goal_contacts = (hi + lo) // 2
    print("Start binary search to max contacts")
    while lo <= hi and goal_contacts <= max_contacts:
        goal_contacts = (hi + lo) // 2
        print(f"Solving {goal_contacts}:", end=" ")
        duration = solve_sat(input_file, goal_contacts, dimension, new)
        total_duration += abs(duration)
        if duration > 0:
            max_contacts = max(max_contacts, goal_contacts)
            lo = goal_contacts + 1
        else:
            hi = goal_contacts - 1
    print()
    return {
        "max_contacts": max_contacts,
        "duration": total_duration,
    }


def solve_sat(input_file: str, goal_contacts: int, dimension: int, new: bool) -> float:
    """
    Run an encoding of the input file, with the target goal of contacts and
    return the duration for solving if it managed
    """
    file_path = encode(input_file, goal_contacts, dimension, new)
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
    print("There was a bug in solving with bule")
    return 0


def encode(input_file: str, goal_contacts: int, dimension: int, new: bool, tracked: bool = False) -> str:
    """
    Generate bule encoding for a protein sequence and write it to a file in
    the models folder, returning the path to the file
    """
    file_name = input_file.split("/")[-1]

    sequence = get_sequence(input_file)
    base_goal = get_adjacent_ones(sequence)
    n = len(sequence)
    w = get_grid_diameter(dimension, n)
    encoding_version = "new" if new else "old"
    in_file = f"models/bul/{file_name}_{encoding_version}.bul"

    # Number of contacts = adjacent "1"s minus offset
    with open(in_file, "w+") as f:
        f.write(f"% {sequence}\n\n")

        f.write(f"% sequence\n")
        for i, c in enumerate(sequence):
            f.write(f"#ground sequence[{i}, {c}].\n")

        f.write("\n% width\n")
        f.write(f"#ground width[{w}].\n\n")

        f.write(f"% Base contacts {base_goal}\n")
        f.write(f"% Goal contacts {goal_contacts}\n")
        f.write(f"#ground goal[{(base_goal + goal_contacts)}].\n\n")

    bule_files_list = [
        f"bule/constraints_{dimension}d_{encoding_version}.bul",
        "bule/cc_a.bul"
    ]

    bule_files = " ".join(bule_files_list)
    out_file = f"models/cnf/{file_name}_{encoding_version}.cnf"
    command = f"bule2 --output dimacs {bule_files} {in_file} > {out_file}"
    subprocess.run(command, shell=True)

    if tracked:
        results_file = f"results/{file_name}_{dimension}d_{encoding_version}.csv"
        print(results_file)
        with open(results_file, "w+") as f:
            f.write("length,time,contacts,variables,clauses\n")
            vars, clauses = get_num_vars_and_clauses(file_name, new)
            f.write(f"{n},0,0,{vars},{clauses}")
    return out_file


def get_num_vars_and_clauses(filename: str, new: bool) -> tuple[int, int]:
    """
    Given the name of the input, return the number of variables and
    clauses in the encoding
    """
    encoding_version = "new" if new else "old"
    with open(f"models/cnf/{filename}_{encoding_version}.cnf") as f:
        return tuple(map(int, f.readline().split()[-2:]))


def get_sequence(input_file: str) -> str:
    """
    Read the input file and return the string sequence of 1s and 0s
    """
    with open(input_file, "r") as f:
        return f.readline().removesuffix("\n")


def get_adjacent_ones(s: str) -> int:
    """
    Return the number of adjacent ones that are in the string
    """
    return [s[i] == s[i+1] == "1" for i in range(len(s)-1)].count(True)


def get_grid_diameter(dimension: int, n: int) -> int:
    """
    Return ideal grid diameter, given the dimension and protein length
    """
    if dimension == 2:
        if n >= 12:
            return 1 + n // 4
        return n
    else:
        if n >= 20:
            return 2 + n // 8
        return 2 + n // 4


def get_max_contacts(s: str) -> int:
    """
    Find the maximum number of contacts that the sequence can have
    """
    n = len(s)
    return sum([s[i+3:n:2].count("1") for i in range(n-3) if s[i] == "1"])


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        type=str,
        help="the path to the input file containing a string of 1s and 0s"
    )
    parser.add_argument(
        "-c", "--contacts",
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
        help="record details such as time, contacts, variables and clauses for a solving an encoding"
    )
    parser.add_argument(
        "-n", "--new",
        action="store_true",
        help="use the new encoding"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
