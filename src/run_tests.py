import argparse
import os
import re
import subprocess
from datetime import datetime

from src.config import TEST_VERSIONS as VERSIONS

MAX_LEN = 23
INPUT_DIR = "./input"
IGNORE: list[str] = []
POLICIES = ["binary_search_policy", "double_binary_policy", "double_linear_policy"]
SOLVERS = ["glucose", "kissat", "minisat"]

def main() -> None:
    args = parse_args()
    dims = [2, 3] if args.dimension == -1 else [args.dimension]
    vers = VERSIONS if args.version == -1 else [args.version]
    for s in get_sequences(INPUT_DIR, args.sequence_type, args.min_len, MAX_LEN):
        print(s)
        match args.test_type:
            case "encoding":
                run_encoding_test(s["filename"], s["seq"], vers, dims)
            case "policy":
                run_policy_test(s["filename"], s["seq"])
            case "solver":
                pass
    print("Finished")


def run_policy_test(filename: str, seq: str) -> None:
    """For the file run a search using different policies"""
    input_file = os.path.join(INPUT_DIR, filename)

    # Run test with just kissat and all policies
    for policy in POLICIES:
        for solver in SOLVERS:
            for v in VERSIONS:
                run_test(input_file, seq, v, 2, solver, policy, "policy")


def run_encoding_test(filename: str, seq: str, vers: list[int], dims: list[int]) -> None:
    """Run a single test using the given filename"""
    input_file = os.path.join(INPUT_DIR, filename)

    for d in dims:
        for v in vers:
            run_test(input_file, seq, v, d, "kissat", "double_linear_policy", "encoding")


def run_test(input_file: str, seq: str, v: int, d: int, solver: str, policy: str, dir: str) -> None:
    
    curr_time = datetime.now().strftime("%H:%M:%S")
    print(f"Testing {input_file}: \t{seq} \t{v = } \t{d = } {curr_time}")
    # We do not solve using the old encoding if 3D and len > 13
    solve = "" if d == 3 and len(seq) >= 13 and v == 0 else "-s"

    command = f"python3 -m src.encode {input_file}"
    options = f"{solve} -t -v {v} -d {d} -p {policy} --solver {solver} -r {dir}"
    subprocess.run((command + " " + options).split(), capture_output=False)


def get_sequences(
    input_dir_name: str,
    seq_type: str,
    min_len: int = 0,
    max_len: int = 100
) -> list[dict[str, str]]:
    """Get list of dicts of sequences and their filename from the input dir"""
    sequences = []
    for filename in os.listdir(input_dir_name):
        if filename in IGNORE or not is_type(filename, seq_type):
            continue

        filepath = os.path.join(input_dir_name, filename)
        with open(filepath) as f:
            sequences.append({"filename": filename, "seq": f.read().removesuffix("\n")})
    # Sort sequence by shortest sequence first
    sequences = [s for s in sequences if len(s["seq"]) >= min_len and len(s["seq"]) < max_len]
    return sorted(sequences, key=lambda x: (len(x["seq"]), x["filename"]))


def get_sequence(filename: str) -> str:
    input_file = os.path.join(INPUT_DIR, filename)
    with open(input_file) as f:
        return f.readline().removeprefix("\n")


def is_type(filename: str, seq_type: str) -> bool:
    """Return if a sequence is real, random, or all (either)"""
    if seq_type == "all":
        return True
    elif seq_type == "real" and re.match("^[a-zA-Z0-9]{6}$", filename):
        return True
    elif seq_type == "random" and filename.startswith("length_"):
        return True
    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dimension",
        nargs="?", type=int, default=-1, choices={2, 3},
        help="the dimension of the embedding grid, default: 2d and 3d"
    )
    parser.add_argument(
        "-m", "--min-len",
        nargs="?", type=int, default=0,
        help="the minimum length sequence to test"
    )
    parser.add_argument(
        "-s", "--sequence-type",
        nargs="?", type=str, default="all", choices={"all", "random", "real"},
        help="the type of protein sequences to test, default value: all"
    )
    parser.add_argument(
        "-t", "--test-type",
        nargs="?", type=str, default="encoding", choices={"encoding", "policy", "solver"},
        help="which independent variable to test"
    )
    parser.add_argument(
        "-v", "--version",
        nargs="?", type=int, default=-1, choices=set(VERSIONS),
        help="the encoding type to test, default: all"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
