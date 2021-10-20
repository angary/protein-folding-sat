# Run "python3 encode.py --solve --time" on multiple input files
# starts with the shortest input sequence first

import os
import subprocess
from typing import List

MAX_LEN = 30
INPUT_DIR = "./input"

# Ignore these inputs
IGNORE = []

def main():
    sequences = get_sequences(INPUT_DIR)
    for sequence in sequences:
        print(sequence)
    for sequence in sequences:
        filename = sequence["filename"]
        string = sequence["string"]
        print(f"Testing {filename}: {string}")
        command = f"python3 encode.py {os.path.join(INPUT_DIR, filename)} --solve --time"
        subprocess.run(command.split(), capture_output=True)
    return


def get_sequences(input_dir_name: str):
    """
    Get a list of the sequences and file names from the input directory
    """
    sequences = []
    for filename in os.listdir(input_dir_name):
        if len(filename) != 6 or filename in IGNORE:
            continue

        filepath = os.path.join(input_dir_name, filename)
        with open(filepath) as f:

            sequence = f.read()[:-1]

            # CURRENTLY IGNORING THINGS THAT LONGER THAN 30
            if len(sequence) >= 30:
                continue

            sequences.append({
                "filename": filename,
                "string": sequence
            })
    
    # Sort sequence by shortest sequence first
    sequences.sort(key=lambda x:len(x["string"]))
    return sequences


if __name__ == "__main__":
    main()
