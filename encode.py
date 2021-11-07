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

    if args.solve and args.time:
        print("Attempting to time and solve\n")
        timed_solve(input_file, dimension, new)
    elif args.solve:
        print("Attempting to solve\n")
        max_contacts = solve(input_file, dimension, new)
        print(f"Max contacts: {max_contacts}")
    elif not args.solve and not args.time:
        print("Attempting to encode\n")
        file_path = encode(input_file, goal_contacts, dimension, new)
        print(f"Encoding bul    : {file_path.replace('cnf', 'bul')}")
        print(f"Encoding kissat : {file_path}")
    else:
        print("Error with options")
    return


def timed_solve(input_file: str, dimension: int, new: bool) -> None:
    """
    Time how long it takes to solve a contact and write it into a file
    """
    length = len(get_sequence(input_file))
    filename = input_file.split("/")[-1]
    encoding_type = "new" if new else "old"
    results_file = f"results/{filename}_{dimension}d_{encoding_type}.csv"

    with open(results_file, "w+") as f:
        f.write("length,time,contacts\n")

    for _ in range(TEST_REPEATS):
        result = solve(input_file, dimension, new)
        max_contacts = result["max_contacts"]
        duration = result["duration"]
        print(results_file)

        with open(results_file, "a") as f:
            f.write(f"{length},{duration},{max_contacts}\n")
    return


def solve(input_file: str, dimension: int, new: bool) -> dict[str, float]:
    """
    Start the goal contacts at 1 and then attempt to solve it, doubling the
    goal contacts until it is unsolvable. Then binary search for the largest
    possible value goal contacts can be whilst solvable and return it.
    """
    # Double goal_contacts until it is unsolvable or it is larger than the
    # length of the sequence
    goal_contacts = 1
    sequence_length = len(get_sequence(input_file))
    total_duration = 0
    print(
        """
        ========================================================================
                                    Start doubling
        ========================================================================
        """
    )
    while goal_contacts < sequence_length:
        print(f"Solving {goal_contacts}: ", end="", flush=True)
        duration = solve_sat(input_file, goal_contacts, dimension, new)
        total_duration += abs(duration)
        solved = duration > 0
        if not solved:
            break
        goal_contacts *= 2
    print(f"Failed to solve at {goal_contacts}")
    print()

    # Binary search to the maximum possible value that the 
    max_contacts = goal_contacts // 2
    lo = goal_contacts // 2 + 1
    hi = goal_contacts - 1
    print(
        """
        ========================================================================
                        Start binary search to max contacts
        ========================================================================
        """
    )
    while lo <= hi:
        # Find the number of contacts
        goal_contacts = (hi + lo) // 2

        # Attempt to solve
        print(f"Solving {goal_contacts}:", end=" ")
        duration = solve_sat(input_file, goal_contacts, dimension, new)
        total_duration += abs(duration)
        solved = duration > 0
        print(solved)

        if solved:
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
    result = subprocess.run(command.split(), capture_output=True)
    duration = time.time() - start
    output = str(result.stdout)
    if "UNSAT" in output:
        print("UNSAT")
        return -duration
    elif "SAT" in output:
        print("SAT")
        return duration
    print("There was a bug in solving with bule")
    return 0
    

def encode(input_file: str, goal_contacts: int, dimension: int, new: bool) -> str:
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
    
    # Number of contacts = adjacent "1"s minus offset
    with open(f"models/{file_name}.bul", "w+") as f:

        # Write sequence string
        f.write(f"% {sequence}\n\n")

        # Write logical encoding of sequence
        f.write(f"% sequence\n")
        # f.write(f"sequence[0..{n - 1}].\n")
        for i, c in enumerate(sequence):
            f.write(f"#ground sequence[{i}, {c}].\n")
        f.write("\n")

        # Write width
        f.write("% width\n")
        f.write(f"#ground width[{w}].\n\n")

        # Write goal contacts
        f.write(f"% Base contacts {base_goal}\n")
        f.write(f"% Goal contacts {goal_contacts}\n")
        f.write(f"#ground goal[{(base_goal + goal_contacts)}].\n\n")

    bule_files_list = [
        f"bule/constraints_{dimension}d_{encoding_version}.bul",
        "bule/cc_a.bul"
    ]

    bule_files = " ".join(bule_files_list)
    in_file = f"models/{file_name}.bul"
    out_file = f"models/{file_name}.cnf"
    command = f"bule2 --output dimacs {bule_files} {in_file} > {out_file}"
    # command = f"bule2 --output qdimacs {bule_files} {in_file} | sed '2d' > {out_file}"
    # command = f"bule2 {bule_files} {in_file} | grep -v exists > {out_file}"
    # bule2 --solve true --solver kissat  bule/constraints_2d_old.bul bule/s_tot.bul models/gen_length_6_1.bul
    subprocess.run(command, shell=True)
    print(out_file)
    return out_file


def get_sequence(input_file: str) -> str:
    """
    Read the input file and return the string sequence of 1s and 0s
    """
    with open(input_file, "r") as f:
        sequence = f.readline()[:-1]  # Ignore last "\n"
    return sequence


def get_adjacent_ones(sequence: str) -> int:
    """
    Return the number of adjacent ones that are in the string
    """
    count = 0
    for i in range(len(sequence) - 1):
        if sequence[i] == "1" and sequence[i + 1] == "1":
            count += 1
    return count


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
        "-c",
        "--contacts",
        nargs="?",
        type=int,
        default=1,
        help="the goal number of (H-H) contacts, default value: 1"
    )
    parser.add_argument(
        "-d",
        "--dimension",
        nargs="?",
        type=int,
        default=2,
        choices={2, 3},
        help="the dimension of the embedding grid, default value: 2"
    )
    parser.add_argument(
        "-s",
        "--solve",
        action="store_true",
        help="solve for the maximum number of contacts"
    )
    parser.add_argument(
        "-t",
        "--time",
        action="store_true",
        help="record the time taken to solve"
    )
    parser.add_argument(
        "-n",
        "--new",
        action="store_true",
        help="use the new encoding"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
