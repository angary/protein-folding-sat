
def main():
    sequence = input("Enter sequence:\n")
    sequence = [x for x in sequence.split() if x.startswith("x")]
    grid = get_grid_from_new(sequence)
    size = len(grid)
    print("Grid: ")
    print("=" * (size + 2))
    for i in reversed(range(size)):
        print(f"|{''.join(grid[i])}|")
    print("=" * (size + 2))


def get_grid_from_old():
    return


def get_grid_from_new(sequence: list[str]) -> list[list[str]]:
    size = max([int(x[4]) for x in sequence]) + 1
    sequence_len = max([int(x[2]) for x in sequence]) + 1

    grid = [[" " for _ in range(size)] for _ in range(size)]

    for i in range(sequence_len):
        i *= 2
        x, y = int(sequence[i][4]), int(sequence[i + 1][4])
        dimension = int(sequence[i][6]), int(sequence[i + 1][6])
        if dimension[0] > dimension[1]:
            x, y = y, x
        grid[y][x] = str(i // 2)
    return grid

if __name__ == "__main__":
    main()
