import subprocess
import os
import pathlib
import csv
from collections import defaultdict

FILEPATH = pathlib.Path(__file__).resolve().parent
BASE_PATH = os.path.join(FILEPATH, "..")

THREADS=[1]

def check_file_matches_parent_dir(filepath):
    """
    Check if a file's name (without suffix) matches its parent directory name.
    """
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    parent_dir = os.path.basename(os.path.dirname(filepath))
    return file_name == parent_dir

if __name__ == "__main__":
    pid = os.getpid()
    cpu_affinity = os.sched_getaffinity(pid)
    mtx_dir = os.path.join(BASE_PATH, "..", "Suitesparse")
    for threads in THREADS:
        with open(f"bench_{threads}thrds.csv", "w") as f:
            f.write("Matrix,Time(ns)\n")
            for file_path in pathlib.Path(mtx_dir).rglob("*"):
                if file_path.is_file() and file_path.suffix == ".mtx" and check_file_matches_parent_dir(file_path):
                    fname = pathlib.Path(file_path).resolve().stem
                    print(f"Benchmarking {fname} with {threads} threads")
                    try:
                        output = subprocess.run([
                            "taskset", "-a", "-c", "0",
                            f"{FILEPATH}/spmv", str(file_path)
                        ], capture_output=True, check=True, text=True).stdout.split("\n")[1]
                        csr5_spmv_exec_time = float(output.split(" ")[1])
                        print(f"Execution time for {fname}: {csr5_spmv_exec_time} ns")
                        f.write(f"{fname},{csr5_spmv_exec_time}\n")
                        f.flush()
                    except subprocess.CalledProcessError as err:
                        print(f"{fname} failed with {err}")
                        continue

    # Merge all bench files into one CSV
    merged_data = defaultdict(list)
    matrix_set = set()

    for threads in THREADS:
        filename = f"bench_{threads}thrds.csv"
        with open(filename, "r") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if row:
                    matrix = row[0]
                    matrix_set.add(matrix)
                    time_val = row[1] if len(row) > 1 else ""
                    merged_data[matrix].append(time_val)

    # Write the merged result
    with open("merged.csv", "w") as merged_file:
        merged_file.write("Matrix")
        for threads in THREADS:
            merged_file.write(f",{threads} Threads")
        merged_file.write("\n")

        for matrix in sorted(matrix_set):
            merged_file.write(matrix)
            times = merged_data.get(matrix, [])
            for time in times:
                merged_file.write(f",{time}")
            # Fill in missing entries if some thread configs failed
            if len(times) < len(THREADS):
                merged_file.write("," * (len(THREADS) - len(times)))
            merged_file.write("\n")
