"""
Visualise embedding of the protein string on the grid given a solved model from
a file. Does not work for at least order

Example:

Input file:
---
x(0,0,0)  x(1,0,1)  x(2,0,2)  x(3,1,2)  x(4,1,1)  x(5,1,0)  x(6,2,0)  x(7,2,1)
---

or

---
Model 1:  y(0,0,0)  y(0,0,1) ~y(0,1,0) ~y(0,1,1) ~y(0,2,0) ~y(0,2,1) ~y(0,3,0) ~y(0,3,1) ~y(0,4,0) ~y(0,4,1) ~y(0,5,0) ~y(0,5,1) ~y(0,6,0) ~y(0,6,1) ~y(0,7,0) ~y(0,7,1)  y(1,0,0)  y(1,0,1) ~y(1,1,0)  y(1,1,1) ~y(1,2,0) ~y(1,2,1) ~y(1,3,0) ~y(1,3,1) ~y(1,4,0) ~y(1,4,1) ~y(1,5,0) ~y(1,5,1) ~y(1,6,0) ~y(1,6,1) ~y(1,7,0) ~y(1,7,1)  y(2,0,0)  y(2,0,1) ~y(2,1,0)  y(2,1,1) ~y(2,2,0)  y(2,2,1) ~y(2,3,0) ~y(2,3,1) ~y(2,4,0) ~y(2,4,1) ~y(2,5,0) ~y(2,5,1) ~y(2,6,0) ~y(2,6,1) ~y(2,7,0) ~y(2,7,1)  y(3,0,0)  y(3,0,1)  y(3,1,0)  y(3,1,1) ~y(3,2,0)  y(3,2,1) ~y(3,3,0) ~y(3,3,1) ~y(3,4,0) ~y(3,4,1) ~y(3,5,0) ~y(3,5,1) ~y(3,6,0) ~y(3,6,1) ~y(3,7,0) ~y(3,7,1)  y(4,0,0)  y(4,0,1)  y(4,1,0)  y(4,1,1) ~y(4,2,0) ~y(4,2,1) ~y(4,3,0) ~y(4,3,1) ~y(4,4,0) ~y(4,4,1) ~y(4,5,0) ~y(4,5,1) ~y(4,6,0) ~y(4,6,1) ~y(4,7,0) ~y(4,7,1)  y(5,0,0)  y(5,0,1)  y(5,1,0) ~y(5,1,1) ~y(5,2,0) ~y(5,2,1) ~y(5,3,0) ~y(5,3,1) ~y(5,4,0) ~y(5,4,1) ~y(5,5,0) ~y(5,5,1) ~y(5,6,0) ~y(5,6,1) ~y(5,7,0) ~y(5,7,1)  y(6,0,0)  y(6,0,1)  y(6,1,0) ~y(6,1,1)  y(6,2,0) ~y(6,2,1) ~y(6,3,0) ~y(6,3,1) ~y(6,4,0) ~y(6,4,1) ~y(6,5,0) ~y(6,5,1) ~y(6,6,0) ~y(6,6,1) ~y(6,7,0) ~y(6,7,1)  y(7,0,0)  y(7,0,1)  y(7,1,0)  y(7,1,1)  y(7,2,0) ~y(7,2,1) ~y(7,3,0) ~y(7,3,1) ~y(7,4,0) ~y(7,4,1) ~y(7,5,0) ~y(7,5,1) ~y(7,6,0) ~y(7,6,1) ~y(7,7,0) ~y(7,7,1)  same(0,1,0) ~same(0,1,1)  same(0,2,0) ~same(0,2,1) ~same(0,3,0) ~same(0,3,1) ~same(0,4,0) ~same(0,4,1) ~same(0,5,0)  same(0,5,1) ~same(0,6,0)  same(0,6,1) ~same(0,7,0) ~same(0,7,1)  same(1,2,0) ~same(1,2,1) ~same(1,3,0) ~same(1,3,1) ~same(1,4,0)  same(1,4,1) ~same(1,5,0) ~same(1,5,1) ~same(1,6,0) ~same(1,6,1) ~same(1,7,0)  same(1,7,1) ~same(2,3,0)  same(2,3,1) ~same(2,4,0) ~same(2,4,1) ~same(2,5,0) ~same(2,5,1) ~same(2,6,0) ~same(2,6,1) ~same(2,7,0) ~same(2,7,1)  same(3,4,0) ~same(3,4,1)  same(3,5,0) ~same(3,5,1) ~same(3,6,0) ~same(3,6,1) ~same(3,7,0) ~same(3,7,1)  same(4,5,0) ~same(4,5,1) ~same(4,6,0) ~same(4,6,1) ~same(4,7,0)  same(4,7,1) ~same(5,6,0)  same(5,6,1) ~same(5,7,0) ~same(5,7,1)  same(6,7,0) ~same(6,7,1) ~next(0,1,0)  next(0,1,1) ~next(1,2,0)  next(1,2,1)  next(1,4,0) ~next(1,4,1) ~next(1,6,0)  next(1,6,1)  next(2,3,0) ~next(2,3,1) ~next(3,4,0)  next(3,4,1) ~next(4,5,0)  next(4,5,1)  next(4,7,0) ~next(4,7,1)  next(5,6,0) ~next(5,6,1) ~next(6,7,0)  next(6,7,1)  var(contact(1,4)) ~var(contact(1,6))  var(contact(4,7))
---

Output (to terminal):

Grid: 
=====
|23 |
|147|
|056|
=====
"""

import re
import sys

from src.util.convert import convert

def main():
    if len(sys.argv) != 2:
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


def get_sequence_embedding(filepath: str) -> str:
    with open(filepath) as f:
        line = f.readlines()[-1]
        if re.match(r"x\(\d,\d,\d\)", line):
            print("HI")
            line = convert(filepath)
            print(line)
        else:
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
    for i, pos in enumerate(sequence):
        pos = pos.split(",")
        x, y = int(pos[1]), int(pos[2].rstrip(")"))
        grid[y][x] = str(i).rjust(max_digits, " ")
    return grid


if __name__ == "__main__":
    main()
