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
    new = args.new

    sequences = get_sequences(INPUT_DIR, seq_type)
    for sequence in sequences:
        print(sequence)
    run_tests(sequences, dimension, new)
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
    return sorted(sequences, key=lambda x:len(x["string"]))


def is_type(filename, seq_type) -> bool:
    if seq_type == "all":
        return True
    elif seq_type == "real" and re.match("^[a-zA-Z0-9]{6}$", filename):
        return True
    elif seq_type == "random" and filename.startswith("length_"):
        return True
    return False


def run_tests(sequences: List[dict], dimension: int, new: bool) -> None:
    for sequence in sequences:
        filename = sequence["filename"]
        string = sequence["string"]

        print(f"Testing {filename}: {string}")

        input_file = os.path.join(INPUT_DIR, filename)
        new_flag = "-n" if new else ""
        command = f"python3 encode.py {input_file} -s -t {new_flag} -d"

        if dimension in [2, 3]:
            command += f" {dimension}"
            subprocess.run(command.split(), capture_output=False)
        else:
            command_2d = command + " 2"
            subprocess.run(command_2d.split(), capture_output=False)
            command_3d = command + " 3"
            subprocess.run(command_3d.split(), capture_output=False)
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
        "-n",
        "--new",
        action="store_true",
        help="use the new encoding"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
