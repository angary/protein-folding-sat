"""
File to find the number of clauses used in count encoding
"""
import math
import subprocess
import tempfile

MAX = 65
COUNT_ENCODING = "counter.bul"

def main():
    results = []
    for i in range(1, MAX):
        # Create a temporary bule file
        with tempfile.NamedTemporaryFile("w+") as f:
            f.writelines([f"#ground cardinality_var[0, {j}]." for j in range(i)])
            f.write(f"#ground cardinality_bound[0, {max(1, i - 2)}].\n")
            f.seek(0)
            # Calculate the number of clauses
            cmd = f"bule2 --output dimacs {f.name} {COUNT_ENCODING} | grep 'p cnf' | cut -d ' ' -f 3-4"
            p = subprocess.run(cmd, capture_output=True, shell=True)
            output = p.stdout.decode().rstrip("\n").replace(" ", ",")
            results.append(f"{i},{output},{2 ** (int(math.log(i, 2)) + 5)}\n")
    with open("calculate_clauses.csv", "w+") as f:
        for res in results:
            f.write(res)


if __name__ == "__main__":
    main()
