import csv
import matplotlib.pyplot as plt
import os

def main():
    dirpath = "./results/input"
    results = {}
    for filepath in os.listdir(dirpath):
        if not filepath.endswith(".csv"):
            continue
        with open(os.path.join(dirpath, filepath)) as f:
            content = f.readlines()
            rows = content[1:]
            csvreader = csv.reader(rows)
            for row in csvreader:
                length = row[0]
                time = float(row[1])
                if length not in results:
                    results[length] = {
                        "total_time": time,
                        "count": 0
                    }
                else:
                    results[length]["total_time"] += time
                    results[length]["count"] += 1
    data = []
    for key in results:
        result = results[key]
        result["total_time"] /= result["count"]
        data.append((int(key), result["total_time"]))

    data.sort(key=lambda x:x[0])
    print(data)
    names = [x[0] for x in data]
    values = [x[1] for x in data]


    plt.plot(names, values, marker="o", label="Original encoding")
    plt.grid(True, which="minor")
    plt.xlabel("Sequence length")
    plt.ylabel("Time(s)")
    plt.yscale("log")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
