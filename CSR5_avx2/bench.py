import subprocess
import os
import pathlib

FILEPATH = pathlib.Path(__file__).resolve().parent
BASE_PATH = os.path.join(FILEPATH)

def check_file_matches_parent_dir(filepath):
    """
    Check if a file's name (without suffix) matches its parent directory name.
    
    Args:
        filepath (str): Full path to the file
        
    Returns:
        bool: True if file name (without suffix) matches parent directory name
        
    Example:
        >>> path = '/local/scratch/a/das160/SABLE/Suitesparse/GD96_a/GD96_a.mtx'
        >>> check_file_matches_parent_dir(path)
        True
    """
    # Get the file name without extension
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    
    # Get the parent directory name
    parent_dir = os.path.basename(os.path.dirname(filepath))
    
    return file_name == parent_dir

if __name__ == "__main__":
    pid = os.getpid()
    cpu_affinity = os.sched_getaffinity(pid)
    mtx_dir = os.path.join("/local", "scratch", "a", "Suitesparse")
    # for threads in [1, 2, 4, 8, 16]:
    for threads in [1]:
        with open("bench_"+str(threads)+"thrds.csv", "w") as f:
            f.write("Matrix,Time(ns)\n")
            for file_path in pathlib.Path(mtx_dir).rglob("*"):
                if file_path.is_file() and file_path.suffix == ".mtx" and check_file_matches_parent_dir(file_path):
                    fname = pathlib.Path(file_path).resolve().stem
                    print(f"Benchmarking {fname} with {threads} threads")
                    f.write(fname)
                    output = subprocess.run(["taskset", "-a", "-c", ",".join([str(x) for x in cpu_affinity]), f"{BASE_PATH}/spmv", str(file_path)], capture_output=True, check=True, text=True)
                    csr5_spmv_exec_time = float(output.stdout.split(" ")[1])
                    f.write(f"{fname},{csr5_spmv_exec_time}\n")
                    f.flush()
                    # try:
                    #     output = subprocess.check_output([f"{BASE_PATH}/build/DDT", "-m", file_path, "-n", op, "-s", "CSR", "--"+benchfile, "-t", str(threads)])
                    # except subprocess.CalledProcessError as err:
                    #     print(fname + " failed with " + str(err))
                    #     continue
                    # psc_times = output.decode("utf-8").split("\n")[:-1]
                    # # Write the output to the file
                    # for time in psc_times:
                    #     f.write(f",{time}")
                    # f.write("\n")
                    # f.flush()
