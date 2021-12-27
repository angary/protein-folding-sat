"""
Visualise embedding of the protein string on the grid given a solved model from
a file.
"""

import sys

def main():
    if len(sys.argv) != 2:
        print("Incorrect usage, needs one argument for the input file path")
        return
    with open(sys.argv[1]) as f:
        line = f.readline()
        sequence = [x for x in line.split() if x.startswith("x")]
        grid = get_grid_from_new(sequence)
        size = len(grid)
        print("Grid: ")
        print("=" * (size + 2))
        for row in reversed(grid):
            print(f"|{''.join(row)}|")
        print("=" * (size + 2))


def get_grid_from_new(sequence: list[str]) -> list[list[str]]:
    """
    Return the grid embedding from the new encoding
    """
    size = max([int(max(x[4], x[6])) for x in sequence]) + 1

    grid = [[" " for _ in range(size)] for _ in range(size)]

    for i, pos in enumerate(sequence):
        x, y = int(pos[4]), int(pos[6])
        grid[y][x] = str(i)
    return grid


if __name__ == "__main__":
    main()
