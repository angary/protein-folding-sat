# Run "python3 encode.py --solve --time" on multiple input files
# starts with the shortest input sequence first

import argparse
import os
import re
import subprocess

from datetime import datetime

MAX_LEN = 30
INPUT_DIR = "./input"

# Ignore these inputs
IGNORE: list[str] = []


def main() -> None:
    args = parse_args()
    dimension = args.dimension
    seq_type = args.type
    encoding_type = args.encoding_type
    min_len = args.min_len

    sequences = get_sequences(INPUT_DIR, seq_type, min_len, MAX_LEN)
    for sequence in sequences:
        print(sequence)
    run_tests(sequences, dimension, encoding_type)


def get_sequences(input_dir_name: str, seq_type: str, min_len: int, max_len: int) -> list[dict[str, str]]:
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


def run_tests(sequences: list[dict], dimension: int, encoding_type: str) -> None:
    """
    Run tests for all the given sequences
    """
    for sequence in sequences:
        filename = sequence["filename"]
        string = sequence["string"]

        new = False if encoding_type == "old" else True
        old = False if encoding_type == "new" else True
        if new:
            run_test(filename, string, True, dimension)
        if old:
            run_test(filename, string, False, dimension)


def run_test(filename: str, string: str, new: bool, dimension: int) -> None:
    """
    Run a single test using the given filename
    """
    input_file = os.path.join(INPUT_DIR, filename)
    new_flag = "-n" if new else ""
    dims = [2, 3] if dimension == 1 else [dimension]
    seq_len = get_seq_len(input_file)

    for dim in dims:
        curr_time = datetime.now().strftime("%H:%M:%S")
        print(f"Testing {input_file}: \t{string} \t{new = } \t{dim = } {curr_time}")

        # We do not solve using the old encoding if 3D and len > 13
        if dim == 3 and seq_len >= 13 and not new:
            command = f"python3 encode.py {input_file} -t {new_flag} -d {dim}"
        else:
            command = f"python3 encode.py {input_file} -s -t {new_flag} -d {dim}"
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
        "-e", "--encoding-type",
        nargs="?", type=str, default="both", choices={"both", "old", "new"},
        help="the encoding type to test, default: new and old"
    )
    parser.add_argument(
        "-m", "--min-len",
        nargs="?", type=int, default=0,
        help="the minimum length sequence to test"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
