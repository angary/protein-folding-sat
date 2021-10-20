"""Take in a string of 1s and 0s and convert it into a bul encoding"""


import argparse
import subprocess
import time

from run_tests import INPUT_DIR


TEST_REPEATS = 3

def main():
    """
    Extract arguments and determine whether to perform an encoding or solve
    """
    args = parse_args()
    input_file = args.input_file
    goal_contacts = args.contacts
    dimension = args.dimension

    if args.solve and args.time:
        print("Attempting to time and solve\n")
        timed_solve(input_file, dimension)
    elif args.solve:
        print("Attempting to solve\n")
        max_contacts = solve(input_file, dimension)
        print(f"Max contacts: {max_contacts}")
    elif not args.solve and not args.time:
        print("Attempting to encode\n")
        file_path = encode(input_file, goal_contacts, dimension)
        print(f"Encoding bul    : {file_path.replace('cnf', 'bul')}")
        print(f"Encoding kissat : {file_path}")
    else:
        print("Error with options")
    return


def timed_solve(input_file: str, dimension: int):
    """
    Time how long it takes to solve a contact and write it into a file
    """
    length = len(get_sequence(input_file))
    filename = input_file.split("/")[-1]
    with open(f"results/{input_file}.csv", "w+") as f:
        f.write("length,time,contacts\n")
    for _ in range(TEST_REPEATS):
        result = solve(input_file, dimension)
        max_contacts = result["max_contacts"]
        duration = result["duration"]
        with open(f"results/{input_file}.csv", "a") as f:
            f.write(f"{length},{duration},{max_contacts}\n")
    return


def solve(input_file: str, dimension: int):
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
        duration = solve_sat(input_file, goal_contacts, dimension)
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
        duration = solve_sat(input_file, goal_contacts, dimension)
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


def solve_sat(input_file: str, goal_contacts: int, dimension: int):
    """
    Run an encoding of the input file, with the target goal of contacts and
    return the duration for solving if it managed
    """
    file_path = encode(input_file, goal_contacts, dimension)
    command = f"kissat {file_path} -q"
    start = time.time()
    result = subprocess.run(command.split(), capture_output=True)
    duration = time.time() - start
    output = str(result.stdout)
    # print(f"{output = }")
    if "UNSAT" in output:
        print("UNSAT")
        return -duration
    elif "SAT" in output:
        print("SAT")
        return duration
    print("There was a bug in solving with bule")


def encode(input_file: str, goal_contacts: int, dimension: int):
    """
    Generate bule encoding for a protein sequence and write it to a file in
    the models folder, returning the path to the file
    """
    file_name = input_file.split("/")[1]

    sequence = get_sequence(input_file)
    base_goal = get_adjacent_ones(sequence)
    n = len(sequence)
    w = get_grid_diameter(dimension, n)
    
    # Number of contacts = adjacent "1"s minus offset
    with open(f"models/{file_name}.bul", "w+") as f:

        # Write sequence string
        f.write(f"% {sequence}\n")
        f.write("\n")

        # Write logical encoding of sequence
        f.write(f"% sequence\n")
        # f.write(f"sequence[0..{n - 1}].\n")
        for i, c in enumerate(sequence):
            f.write(f"#ground sequence[{i}, {c}].\n")
        f.write("\n")

        # Write width
        f.write("% width\n")
        f.write(f"#ground width[{w}].\n")
        f.write("\n")

        # Write goal contacts
        f.write(f"% Base contacts {base_goal}\n")
        f.write(f"% Goal contacts {goal_contacts}\n")
        f.write(f"#ground goal[{(base_goal + goal_contacts)}].\n")
        f.write("\n")

    bule_files_list = [
        "bule/constraints.bul",
        "bule/cc_a.bul"
    ]

    bule_files = " ".join(bule_files_list)
    in_file = f"models/{file_name}.bul"
    out_file = f"models/{file_name}.cnf"
    command = f"bule2 --output dimacs {bule_files} {in_file} > {out_file}"
    # command = f"bule2 --output qdimacs {bule_files} {in_file} | sed '2d' > {out_file}"
    # command = f"bule2 --output qdimacs {bule_files} {in_file} | sed '2d' > {out_file}"
    # command = f"bule2 {bule_files} {in_file} | grep -v exists > {out_file}"
    # bule2 --solve true --solver kissat  bule/constraints.bul bule/sort_tot.bul bule/order.bul models/gen_length_6_1.bul
    subprocess.run(command, shell=True)
    print(out_file)
    return out_file


def get_sequence(input_file: str):
    """
    Read the input file and return the string sequence of 1s and 0s
    """
    sequence = ""
    with open(input_file, "r") as f:
        sequence = f.readline()[:-1] # Ignore last "\n"
    return sequence


def get_adjacent_ones(sequence: str):
    """
    Return the number of adjacent ones that are in the string
    """
    count = 0
    for i in range(len(sequence) - 1):
        if sequence[i] == "1" and sequence[i + 1] == "1":
            count += 1
    return count


def get_grid_diameter(dimension: int, n: int):
    """
    Return ideal grid diameter, given the dimension and protein length
    """
    w = 0
    if dimension == 2:
        if n >= 12:
            w = 1 + n // 4
        else:
            w = n
    else:
        if n >= 20:
            w = 2 + n // 8 
        else:
            w = 2 + n // 4
    return w


def find_offset(sequence: str):
    """
    Return the number of adjacent "1"s in the sequence
    """
    n = len(sequence)
    count = 0
    for i in range(n - 1):
        if sequence[i] == "1" and sequence[i] == sequence[i + 1]:
            count += 1
    return count


def parse_args():
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
    return parser.parse_args()


if __name__ == "__main__":
    main()
