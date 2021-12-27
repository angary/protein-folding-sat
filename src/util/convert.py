"""
Given the path to a solved model of at least v2 (OrderEncoding + dimension
reduction) or newer encoding, convert it into the original encoding output.
Only works for 2D embeddings

Example input file:
---
Instance ground. Starts solving
Model 1:  y(0,0,0)  y(0,0,1)  y(1,0,0)  y(1,0,1)  y(1,1,1)  y(2,0,0)  y(2,0,1)  y(2,1,1)  y(2,2,1)  y(3,0,0)  y(3,0,1)  y(3,1,1)  y(3,2,1)  y(3,3,1)  y(4,0,0)  y(4,0,1)  y(4,1,0)  y(4,1,1)  y(4,2,1)  y(4,3,1)  y(5,0,0)  y(5,0,1)  y(5,1,0)  y(5,1,1)  y(5,2,1)  var(contact(2,5))
---

Example output file:
---
x(0,0,0)  x(1,0,1)  x(2,0,2)  x(3,0,3)  x(4,1,3)  x(5,1,2)
---

"""

import sys


def main():
    if len(sys.argv) != 2:
        print("invalid number of arguments")
        return
    
    xs = []
    with open(sys.argv[1]) as f:
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
            curr_index = int(pos[2])
            pos_in_dim = int(pos[4])
            dimension = int(pos[6])
            if curr_index > index:
                xs.append(index_position.copy())
                index += 1
            else:
                index_position[dimension] = pos_in_dim
        xs.append(index_position.copy())
    
    output_arr = [f"x({i},{x},{y})" for i, (x, y) in enumerate(xs)]
    output_str = "  ".join(output_arr)

    with open("new.temp.bul", "w+") as f:
        f.write(output_str + "\n")


if __name__ == "__main__":
    main()
