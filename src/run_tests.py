# Run "python3 encode.py --solve --time" on multiple input files
# starts with the shortest input sequence first

import argparse
import os
import re
import subprocess
from datetime import datetime

MAX_LEN = 30
INPUT_DIR = "./input"
VERSIONS: list[int] = [0, 1, 2]
IGNORE: list[str] = []


def main() -> None:
    args = parse_args()
    dimension = args.dimension
    seq_type = args.type
    version = args.version
    min_len = args.min_len

    sequences = get_sequences(INPUT_DIR, seq_type, min_len, MAX_LEN)
    for sequence in sequences:
        print(sequence)
    run_tests(sequences, dimension, version)


def get_sequences(
    input_dir_name: str,
    seq_type: str,
    min_len: int = 0,
    max_len: int = 100
) -> list[dict[str, str]]:
    """
    Get a list of dictionaries containing sequences and their filename
    from the input directory
    """
    sequences = []
    for filename in os.listdir(input_dir_name):
        if filename in IGNORE or not is_type(filename, seq_type):
            continue

        filepath = os.path.join(input_dir_name, filename)
        with open(filepath) as f:
            sequence = f.read()[:-1]
            sequences.append({
                "filename": filename,
                "string": sequence
            })
    # Sort sequence by shortest sequence first
    sequences = [s for s in sequences if len(s["string"]) >= min_len and len(s["string"]) < max_len]
    return sorted(sequences, key=lambda x: (len(x["string"]), x["filename"]))


def is_type(filename: str, seq_type: str) -> bool:
    """
    Return if a sequence is real, random, or all
    """
    if seq_type == "all":
        return True
    elif seq_type == "real" and re.match("^[a-zA-Z0-9]{6}$", filename):
        return True
    elif seq_type == "random" and filename.startswith("length_"):
        return True
    return False


def run_tests(sequences: list[dict], dimension: int, version: int) -> None:
    """
    Run tests for all the given sequences
    """
    for sequence in sequences:
        filename = sequence["filename"]
        string = sequence["string"]

        run_test(filename, string, version, dimension)


def run_test(filename: str, string: str, version: int, dimension: int) -> None:
    """
    Run a single test using the given filename
    """
    input_file = os.path.join(INPUT_DIR, filename)
    dims = [2, 3] if dimension == 1 else [dimension]
    seq_len = get_seq_len(input_file)

    if version == -1:
        versions = VERSIONS
    else:
        versions = [version]
    for v in versions:
        for dim in dims:
            curr_time = datetime.now().strftime("%H:%M:%S")
            print(f"Testing {input_file}: \t{string} \t{version = } \t{dim = } {curr_time}")

            # We do not solve using the old encoding if 3D and len > 13
            solve = "" if dim == 3 and seq_len >= 13 and v == 0 else "-s"
            command = f"python3 encode.py {input_file} {solve} -t -v {v} -d {dim}"
    subprocess.run(command.split(), capture_output=False)


def get_seq_len(input_file: str) -> int:
    """
    Given a file to a sequence, return the length of the sequence
    """
    with open(input_file) as f:
        return len(f.readline().removesuffix("\n"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--dimension",
        nargs="?", type=int, default=1, choices={2, 3},
        help="the dimension of the embedding grid, default: 2d and 3d"
    )
    parser.add_argument(
        "-t", "--type",
        nargs="?", type=str, default="all", choices={"all", "random", "real"},
        help="the type of protein sequences to test, default value: all"
    )
    parser.add_argument(
        "-v", "--version",
        nargs="?", type=int, default=-1, choices=set(VERSIONS),
        help="the encoding type to test, default: all"
    )
    parser.add_argument(
        "-m", "--min-len",
        nargs="?", type=int, default=0,
        help="the minimum length sequence to test"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
