import os
import subprocess

MAX_LEN = 30

def main():
    sequences = get_sequences("./input")
    for sequence in sequences:
        filename = sequence["filename"]
        string = sequence["string"]
        print(f"Testing {filename}: {string}")
        command = f"python3 encode.py input/{filename} --solve --time"
        subprocess.run(command.split(), capture_output=True)

    
    return


def get_sequences(input_dir_name: str) -> list:
    sequences = []
    for filename in os.listdir(input_dir_name):
        if len(filename) != 6:
            continue

        filepath = os.path.join(input_dir_name, filename)

        with open(filepath) as f:

            sequence = f.read()[:-1]
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
