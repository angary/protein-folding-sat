def main1():
    results = []
    with open("temp_new") as f:
        lines = f.readlines()
        for i in range(1, len(lines) - 1):
            line = lines[i]
            try:
                start = line.index("x")
            except:
                return
            if start == 0:
                print("new already converted")
                return
            # if "n" in line:
            #     end = line.index("n") - 1
            # else:
            #     end = len(line) - 1
            # extra = line[end:].rstrip("\n")
            line = line[start:].split()
            xs = [val for val in line if val.startswith("x")]
            result = []
            for j in range(0, len(xs), 2):
                # a is the var of the lower dimension
                a = xs[j]
                b = xs[j + 1]
                if a[-2] > b[-2]:
                    a, b = b, a
                point = a[2]
                x = a[4]
                y = b[4]
                result.append(f"x({point},c({x},{y}))")
            
            extras = " ".join(line[len(xs):])
            results.append("  ".join(result) + "\n")
            # results.append("  ".join(result) + " " + extras + "\n")
    results.sort()
    for result in results:
        print(result)
    with open("temp_new", "w+") as f:
        f.writelines(results)

def main2():
    results = []
    with open("temp_old") as f:
        lines = f.readlines()
        for i in range(1, len(lines) - 1):
            line = lines[i]
            try:
                start = line.index("x")
            except:
                return
            if start == 0:
                print("old already converted")
                return
            line = line[start:]
            results.append(line)

    results.sort()
    with open("temp_old", "w+") as f:
        f.writelines(results)


if __name__ == "__main__":
    main1()
    main2()
