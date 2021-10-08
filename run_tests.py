import os


def main():
    max_len = 20
    input_dir_name = "./input"


    # Read all the files in the input directory
    for filename in os.listdir(input_dir_name):

        if len(filename) != 6:
            continue
        filepath = os.path.join(input_dir_name, filename)
        with open(filepath) as f:
            sequence = f.read()[:-1]
            if len(sequence) < max_len:
                print(filename)
                print(len(sequence))
                print(sequence)
                print()
    return


if __name__ == "__main__":
    main()
