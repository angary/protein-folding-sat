# Plot the runtime results for the encodings

import csv
import matplotlib.pyplot as plt
import os

OLD_2D = 0
NEW_2D = 1
OLD_3D = 2
NEW_3D = 3

def main():
    dirpath = "./results"
    all_results = [{}, {}, {}, {}]
    for filepath in os.listdir(dirpath):
        if not filepath.endswith(".csv"):
            continue
        with open(os.path.join(dirpath, filepath)) as f:
            content = f.readlines()
            rows = csv.reader(content[1:])
            for row in rows:
                length = row[0]
                time = float(row[1])

                # Find teh type of result
                if "_2d" in filepath:
                    result_type = OLD_2D
                else:
                    result_type = OLD_3D
                
                # Add or increment the result
                results = all_results[result_type]
                if length not in results:
                    results[length] = {
                        "total_time": time,
                        "count": 0
                    }
                else:
                    results[length]["total_time"] += time
                    results[length]["count"] += 1
    
    all_data = []

    for results in all_results:
        data = []
        for key in results:
            result = results[key]
            result["total_time"] /= result["count"]
            data.append((int(key), result["total_time"]))
        all_data.append(data)

    for data in all_data:
        data.sort(key=lambda x:x[0])
        print(data)
    

    names = [x[0] for x in all_data[OLD_2D]]
    values = [x[1] for x in all_data[OLD_2D]]
    plt.plot(names, values, marker="o", label="Original 2d encoding")

    names = [x[0] for x in all_data[OLD_3D]]
    values = [x[1] for x in all_data[OLD_3D]]
    plt.plot(names, values, marker="o", label="Original 3d encoding")

    plt.grid(True, which="minor")
    plt.xlabel("Sequence length")
    plt.xticks(names)
    plt.ylabel("Time(s)")
    plt.yscale("log")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
