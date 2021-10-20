# Compare produced test results with expected test results

import csv
import os
import sys

EXPECTED = "expected/"


def main():
    output_dir = "results/input"
    if len(sys.argv) >= 2:
        output_dir = os.path.join(output_dir, sys.argv[1])

    # Read each file in the results dir
    sequences = []
    for filename in os.listdir(output_dir):
        if not filename.endswith(".csv"):
            continue
        sequence_name = filename.rstrip(".csv")
        with open(os.path.join(output_dir, filename)) as f:
            content = f.readlines()
            rows = list(csv.reader(content[1:]))
            if len(rows) < 1:
                continue
            contacts = rows[0][-1]
            sequences.append({
                "name": sequence_name,
                "contacts": int(contacts)
            })

    # Check if the sequence is correct
    for sequence in sequences:
        filename = f"{sequence['name']}_opt.txt"
        filepath = os.path.join(EXPECTED, filename)
        with open(filepath) as f:
            f.readline() # Ignore random newline
            expected_contacts  = int(f.readline().split()[-1])
            correct = sequence["contacts"] == expected_contacts
            print(f"Correct result for {sequence['name']}: {correct}")
    return


if __name__ == "__main__":
    main()
