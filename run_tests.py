# Run "python3 encode.py --solve --time" on multiple input files
# starts with the shortest input sequence first

import argparse
import os
import re
import subprocess
import sys

from typing import List

MAX_LEN = 30
INPUT_DIR = "./input"

# Ignore these inputs
IGNORE = []

def main() -> None:
    args = parse_args()
    dimension = args.dimension
    seq_type = args.type
    encoding_type = args.encoding_type

    sequences = get_sequences(INPUT_DIR, seq_type)
    for sequence in sequences:
        print(sequence)
    run_tests(sequences, dimension, encoding_type)
    return


def get_sequences(input_dir_name: str, seq_type: str) -> list[dict[str, str]]:
    """
    Get a list of the sequences and file names from the input directory
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
    return sorted(sequences, key=lambda x: (len(x["string"]), x["filename"]))


def is_type(filename, seq_type) -> bool:
    if seq_type == "all":
        return True
    elif seq_type == "real" and re.match("^[a-zA-Z0-9]{6}$", filename):
        return True
    elif seq_type == "random" and filename.startswith("length_"):
        return True
    return False


def run_tests(sequences: List[dict], dimension: int, encoding_type: str) -> None:
    for sequence in sequences:
        filename = sequence["filename"]
        string = sequence["string"]

        new = False if encoding_type == "old" else True
        old = False if encoding_type == "new" else True
        if new:
            run_test(filename, string, True, dimension)
        if old:
            run_test(filename, string, False, dimension)
    return


def run_test(filename: str, string: str, new: bool, dimension: int) -> None:
    input_file = os.path.join(INPUT_DIR, filename)

    new_flag = "-n" if new else ""

    if dimension == 1:
        dims = [2, 3]
    else:
        dims = [dimension]

    for dim in dims:
        print(f"Testing {input_file}: \t{string} \t{new = } \t{dim = }")
        command = f"python3 encode.py {input_file} -s -t {new_flag} -d {dim}"
        subprocess.run(command.split(), capture_output=True)
    return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--dimension",
        nargs="?",
        type=int,
        default=1,
        choices={2, 3},
        help="the dimension of the embedding grid, by default it will test both"
    )
    parser.add_argument(
        "-t",
        "--type",
        nargs="?",
        type=str,
        default="all",
        choices={"all", "random", "real"},
        help="the type of protein sequences to test, default value: all"
    )
    parser.add_argument(
        "-e",
        "--encoding-type",
        nargs="?",
        type=str,
        default="both",
        choices={"both", "old", "new"},
        help="the encoding type to test"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
