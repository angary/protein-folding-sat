"""
Visualise embedding of the protein string on the grid given a solved model from
a file. Does not work for at least order

Example:

Input file:
---
Model 1:  x(0,c(4,1))  x(1,c(5,1))  x(10,c(0,3))  x(11,c(0,4))  x(12,c(1,4))  x(13,c(1,5))  x(14,c(2,5))  x(15,c(2,4))  x(16,c(2,3))  x(17,c(3,3))  x(18,c(4,3))  x(19,c(4,4))  x(2,c(5,2))  x(20,c(3,4))  x(3,c(4,2))  x(4,c(3,2))  x(5,c(2,2))  x(6,c(2,1))  x(7,c(1,1))  x(8,c(1,2))  x(9,c(1,3))
---

Output (to terminal):

----
Grid: 
====================
|    13 14         |
| 11 12 15 20 19   |
| 10  9 16 17 18   |
|     8  5  4  3  2|
|     7  6     0  1|
|                  |
====================
---
"""
from __future__ import annotations

import re
import sys

from src.util.convert import convert

def main():
    if len(sys.argv) < 2:
        print("Incorrect usage, needs one argument for the input file path")
        return
    sequence = get_sequence_embedding(sys.argv[1])
    grid = get_grid_from_new(sequence)
    size = len(grid)
    print("Grid: ")
    print("=" * (size * (len(str(len(sequence))) + 1) + 2))
    for row in reversed(grid):
        print(f"|{''.join(row)}|")
    print("=" * (size * (len(str(len(sequence))) + 1) + 2))

    if len(sys.argv) == 3:
        print("=" * (len(grid[0] * 2) + 1))
        binary_sequence = sys.argv[2]
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                char = grid[i][j].strip()
                if char.isdigit():
                    grid[i][j] = binary_sequence[int(char)]
                else:
                    grid[i][j] = " "
        for row in reversed(grid):
            print(f"|{' '.join(row)}|")
        print("=" * (len(grid[0] * 2) + 1))

def get_sequence_embedding(filepath: str) -> str:
    with open(filepath) as f:
        line = f.readlines()[-1]

        if re.match(r"x\(\d,\d,\d\)", line):
            # v1 encoding
            line = convert(filepath)
        else:
            # v0 encdoing
            line = [x for x in line.split() if x.startswith("x")]
            line = [x.replace("c(","").replace("))",")") for x in line]
        return line


def get_grid_from_new(sequence: list[str]) -> list[list[str]]:
    """
    Return the grid embedding from the new encoding
    """
    size = max([int(max(x.split(",")[1], x.split(",")[2].rstrip(")"))) for x in sequence]) + 1

    max_digits = len(str(len(sequence))) + 1
    padding = " " * max_digits
    grid = [[padding for _ in range(size)] for _ in range(size)]

    # Sort the sequence by index
    sequence.sort(key=lambda x:int(x.split(",")[0].lstrip("x(")))
    for i, pos in enumerate(sequence):
        pos = pos.split(",")
        x, y = int(pos[1]), int(pos[2].rstrip(")"))
        grid[y][x] = str(i).rjust(max_digits, " ")
    return grid


if __name__ == "__main__":
    main()
