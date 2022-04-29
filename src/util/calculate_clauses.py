"""
File to find the number of clauses used in cca encoding
"""
import math
import subprocess
import tempfile

MAX = 200
ENCODING = "counter"
BULE_FILE = f"bule/{ENCODING}.bul"

def main():
    results = []
    for i in range(1, MAX):
        print(i)
        # Create a temporary bule file
        with tempfile.NamedTemporaryFile("w+") as f:
            f.writelines([f"#ground cardinality_var[0, {j}]." for j in range(i)])
            f.write(f"#ground cardinality_bound[0, {max(1, i - 2)}].\n")
            f.seek(0)
            # Calculate the number of clauses
            cmd = f"bule --output dimacs {f.name} {BULE_FILE} | grep 'p cnf' | cut -d ' ' -f 3-4"
            p = subprocess.run(cmd, capture_output=True, shell=True)
            output = p.stdout.decode().rstrip("\n").replace(" ", ",")
            results.append(f"{i},{output}\n")
    with open(f"calculate_clauses-{ENCODING}.csv", "w+") as f:
        f.write("i,variables,clauses")
        for res in results:
            f.write(res)

    return


if __name__ == "__main__":
    main()
