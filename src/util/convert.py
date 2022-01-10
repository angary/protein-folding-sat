"""
Given the path to a solved model of at least v2 (OrderEncoding + dimension
reduction) or newer encoding, convert it into the original encoding output.
Only works for 2D embeddings

Example input file:
---
Instance ground. Starts solving
Model 1:  y(0,0,0)  y(0,0,1) ~y(0,1,0) ~y(0,1,1) ~y(0,2,0) ~y(0,2,1) ~y(0,3,0) ~y(0,3,1) ~y(0,4,0) ~y(0,4,1) ~y(0,5,0) ~y(0,5,1) ~y(0,6,0) ~y(0,6,1) ~y(0,7,0) ~y(0,7,1)  y(1,0,0)  y(1,0,1) ~y(1,1,0)  y(1,1,1) ~y(1,2,0) ~y(1,2,1) ~y(1,3,0) ~y(1,3,1) ~y(1,4,0) ~y(1,4,1) ~y(1,5,0) ~y(1,5,1) ~y(1,6,0) ~y(1,6,1) ~y(1,7,0) ~y(1,7,1)  y(2,0,0)  y(2,0,1) ~y(2,1,0)  y(2,1,1) ~y(2,2,0)  y(2,2,1) ~y(2,3,0) ~y(2,3,1) ~y(2,4,0) ~y(2,4,1) ~y(2,5,0) ~y(2,5,1) ~y(2,6,0) ~y(2,6,1) ~y(2,7,0) ~y(2,7,1)  y(3,0,0)  y(3,0,1)  y(3,1,0)  y(3,1,1) ~y(3,2,0)  y(3,2,1) ~y(3,3,0) ~y(3,3,1) ~y(3,4,0) ~y(3,4,1) ~y(3,5,0) ~y(3,5,1) ~y(3,6,0) ~y(3,6,1) ~y(3,7,0) ~y(3,7,1)  y(4,0,0)  y(4,0,1)  y(4,1,0)  y(4,1,1) ~y(4,2,0) ~y(4,2,1) ~y(4,3,0) ~y(4,3,1) ~y(4,4,0) ~y(4,4,1) ~y(4,5,0) ~y(4,5,1) ~y(4,6,0) ~y(4,6,1) ~y(4,7,0) ~y(4,7,1)  y(5,0,0)  y(5,0,1)  y(5,1,0) ~y(5,1,1) ~y(5,2,0) ~y(5,2,1) ~y(5,3,0) ~y(5,3,1) ~y(5,4,0) ~y(5,4,1) ~y(5,5,0) ~y(5,5,1) ~y(5,6,0) ~y(5,6,1) ~y(5,7,0) ~y(5,7,1)  y(6,0,0)  y(6,0,1)  y(6,1,0) ~y(6,1,1)  y(6,2,0) ~y(6,2,1) ~y(6,3,0) ~y(6,3,1) ~y(6,4,0) ~y(6,4,1) ~y(6,5,0) ~y(6,5,1) ~y(6,6,0) ~y(6,6,1) ~y(6,7,0) ~y(6,7,1)  y(7,0,0)  y(7,0,1)  y(7,1,0)  y(7,1,1)  y(7,2,0) ~y(7,2,1) ~y(7,3,0) ~y(7,3,1) ~y(7,4,0) ~y(7,4,1) ~y(7,5,0) ~y(7,5,1) ~y(7,6,0) ~y(7,6,1) ~y(7,7,0) ~y(7,7,1)  same(0,1,0) ~same(0,1,1)  same(0,2,0) ~same(0,2,1) ~same(0,3,0) ~same(0,3,1) ~same(0,4,0) ~same(0,4,1) ~same(0,5,0)  same(0,5,1) ~same(0,6,0)  same(0,6,1) ~same(0,7,0) ~same(0,7,1)  same(1,2,0) ~same(1,2,1) ~same(1,3,0) ~same(1,3,1) ~same(1,4,0)  same(1,4,1) ~same(1,5,0) ~same(1,5,1) ~same(1,6,0) ~same(1,6,1) ~same(1,7,0)  same(1,7,1) ~same(2,3,0)  same(2,3,1) ~same(2,4,0) ~same(2,4,1) ~same(2,5,0) ~same(2,5,1) ~same(2,6,0) ~same(2,6,1) ~same(2,7,0) ~same(2,7,1)  same(3,4,0) ~same(3,4,1)  same(3,5,0) ~same(3,5,1) ~same(3,6,0) ~same(3,6,1) ~same(3,7,0) ~same(3,7,1)  same(4,5,0) ~same(4,5,1) ~same(4,6,0) ~same(4,6,1) ~same(4,7,0)  same(4,7,1) ~same(5,6,0)  same(5,6,1) ~same(5,7,0) ~same(5,7,1)  same(6,7,0) ~same(6,7,1) ~next(0,1,0)  next(0,1,1) ~next(1,2,0)  next(1,2,1)  next(1,4,0) ~next(1,4,1) ~next(1,6,0)  next(1,6,1)  next(2,3,0) ~next(2,3,1) ~next(3,4,0)  next(3,4,1) ~next(4,5,0)  next(4,5,1)  next(4,7,0) ~next(4,7,1)  next(5,6,0) ~next(5,6,1) ~next(6,7,0)  next(6,7,1)  var(contact(1,4)) ~var(contact(1,6))  var(contact(4,7))

Example output file:
---
x(0,0,0)  x(1,0,1)  x(2,0,2)  x(3,1,2)  x(4,1,1)  x(5,1,0)  x(6,2,0)  x(7,2,1)
---

"""

import sys


def main():
    if len(sys.argv) != 2:
        print("invalid number of arguments")
        return
    output_str = convert(sys.argv[1])
    with open("new.temp.bul", "w+") as f:
        f.write(output_str + "\n")


def convert(filepath: str) -> str:
    xs = []
    with open(filepath) as f:
        f.readline() # Ignore the "Instance ground. Starts solving" line

        # Extract out where each index is "at least"
        positions = [p for p in f.readline().split() if p.startswith("y")]

        # Sort it by index, then its position, then its dimension
        positions.sort()

        # `index` is the current index we are at, and `index_position` is it's 
        # x and y coordinate on the grid
        index = 0
        index_position = [0, 0]
        for pos in positions:
            pos = pos.split(",")
            curr_index = int(pos[0].lstrip("y("))
            pos_in_dim = int(pos[1])
            dimension = int(pos[2].rstrip(")"))
            if curr_index > index:
                xs.append(index_position.copy())
                index += 1
            else:
                index_position[dimension] = pos_in_dim
        xs.append(index_position.copy())
    
    output_arr = [f"x({i},{x},{y})" for i, (x, y) in enumerate(xs)]
    return "  ".join(output_arr)


if __name__ == "__main__":
    main()
