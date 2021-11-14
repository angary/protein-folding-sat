# Hannah Brown, 10/20/19
# Generates binary sequence files for each file in the Dataset directory
# These input files can later be used for the HPsat and pipeline programs

import sys
import os

from pathlib import Path


def write_binary_sequence_and_contact_number(read_file: Path, output_file: Path) -> None:
    with open(output_file, "w") as f:
        file_contents = read_file.read_text()
        remarks = file_contents.split("REMARK")

        for i, x in enumerate(remarks):
            line = x.strip()
            remarks[i] = line

        for i, x in enumerate(remarks):
            if remarks[i-1].find("Native sequence") != -1:
                original_sequence = ""

                while len(remarks[i]) > 0:
                    original_sequence += remarks[i]
                    i += 1
            elif x.find("*") != -1:
                coord_str = x[1:]

                while len(remarks[i+1]) > 0:
                    coord_str += remarks[i+1]
                    i += 1
                break

        binary_sequence = get_binary_sequence(original_sequence)
        coords = get_coordinates(coord_str)
        num_contacts = count_contacts(coords, binary_sequence)
        print(binary_sequence, file=f)
        # print("\n" + str(num_contacts), file=f)


def get_binary_sequence(amino_acid_sequence: str) -> str:
    ONES = ['A', 'C', 'G', 'I', 'L', 'M', 'F', 'P', 'W', 'Y', 'V']
    ZEROS = ['R', 'N', 'D', 'Q', 'E', 'H', 'K', 'S', 'T']

    sequence = ""

    for x in amino_acid_sequence:
        if x in ONES:
            sequence += "1"
        elif x in ZEROS:
            sequence += "0"
        else:
            raise Exception("ERROR: invalid character in sequence: {x}")

    return sequence


def get_coordinates(coord_str) -> list[list[int]]:
    coords = list()
    coords.append([0,0,0])

    for i, c in enumerate(coord_str):
        coord = list(coords[i])

        if c == "L":
            coord[0] += 1
        elif c == "R":
            coord[0] -= 1
        elif c == "F":
            coord[1] += 1
        elif c == "B":
            coord[1] -= 1
        elif c == "U":
            coord[2] += 1
        elif c == "D":
            coord[2] -= 1
        else:
            raise Exception("Error: unrecognized coordinate character: {c}")

        coords.append(coord)

    return coords


def count_contacts(coords: list[list[int]], string: str) -> int:
    contacts = 0

    for i, x in enumerate(coords):
        if string[i] == "0":
            continue
        for j, y in enumerate(coords[i+3:]):
            if string[i+3+j] == "0":
                continue
            if x[0] == y[0] and x[1] == y[1] and abs(x[2] - y[2]) == 1:
                contacts += 1
            elif x[0] == y[0] and x[2] == y[2] and abs(x[1] - y[1]) == 1:
                contacts += 1
            elif x[1] == y[1] and x[2] == y[2] and abs(x[0] - y[0]) == 1:
                contacts += 1
    return contacts


def main(argv: list[str]) -> None:
    if (len(argv) < 2 or len == 3):
        raise Exception("ERROR: Usage\n\tpython3 get_sequences.py {file/directory to read from} {flag (-d(irectory) or -f(ile))} {file type (if flag = -d)}")
    elif len(argv) == 4:
        filter = argv[3]
        flag = argv[2]
        directory = Path(argv[1])
    else:
        flag = "-f"
        file = Path("./Dataset/" + argv[1] + "_cubic.pdb")
        out_file = Path("./input/" + argv[1])

    if flag == "-d": # loop through directory
        directory_contents = os.listdir(directory)

        for x in directory_contents:
            if x.find(filter) != -1:
                dash_index = x.rfind("_")
                if dash_index != -1:
                    out_file = Path("input/" + x[:dash_index])
                else:
                    out_file = Path("input/" + x)
                print(x)
                write_binary_sequence_and_contact_number(directory / Path(x), out_file)
    else:
        print(file)
        print(out_file)
        write_binary_sequence_and_contact_number(file, out_file)

    # parse the remarks and assign original_sequence and coordinates


if __name__ == "__main__":
    main(["get_sequences.py", "Dataset", "-d", ".pdb"])


"""
A     1
R     0
N     0
D     0
C     1
Q     0
E     0
G     1
H     0
I     1
L     1
K     0
M     1
F     1
P     1
S     0
T     0
W     1
Y     1
V     1
"""
