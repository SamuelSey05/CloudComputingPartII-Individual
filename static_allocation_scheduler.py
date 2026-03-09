import argparse
import csv
from datetime import datetime
import os
import re
import subprocess
from pathlib import Path

SPARK_SUBMIT_BASH = "./submit.sh"
BASH_OUTPUT_FILENAME = "./execution_time.txt"
TIMESTAMP = datetime.now().strftime("%Y%m%dT%H%M%S")
OUTPUT_CSV = Path("static.csv")

def estimate_time(size: int, executors: float) -> float:
    """
    Function to estimate the time taken to run WordLetterCount on a certain filesize with a certain number of executors
    :param size: Size of file
    :param executors: Number of executors
    :return: Estimated time
    """

    return 29.0 + (0.241 * size) / executors + 0.00261 * size

def calculate_optimum_executors_allocation_cutoff(size, max_executors, threshold=0.05):

    for n in range(1, max_executors):
        current_time = estimate_time(size, n)
        next_time = estimate_time(size, n+1)

        improvement = (current_time - next_time) / current_time

        if improvement < threshold:
            return n, current_time

    # Resort to max_executors
    return max_executors, estimate_time(size, max_executors)


def calculate_optimum_executors_allocation(size):
    predicted_no_ex = float('inf')
    predicted_ex_time = estimate_time(size, predicted_no_ex)

    return predicted_no_ex, predicted_ex_time

def main():
    argparser = argparse.ArgumentParser(description="Static Allocation Scheduler")

    argparser.add_argument("input_file", type=str, help="Path to input file")
    argparser.add_argument("--cutoff_scheduler", action="store_true", help="Whether to use cutoff scheduler or not")

    args = argparser.parse_args()


    if not OUTPUT_CSV.exists():
        with open(OUTPUT_CSV, "w") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "Input_File_in_MB", "predicted_no_ex", "predicted_ex_time", "assigned_no_ex", "measured_ex_time"])

    match = re.search(r'(\d+)MB', args.input_file)

    if match:
        file_size = int(match.group(1))
    else:
        raise ValueError("Could not parse file size from input_file. Please pass file in the form \"/test-data/data_XXXMB.txt\"")

    if args.cutoff_scheduler:
         print("Using cutoff scheduler with 5% improvement threshold.")
         predicted_no_ex, predicted_ex_time = calculate_optimum_executors_allocation_cutoff(file_size, 30)
    else:
        print("Using simple scheduler with max 10 executors.")
        predicted_no_ex, predicted_ex_time = calculate_optimum_executors_allocation(file_size)


    # Cap actual executors to 10 as per the problem statement
    assigned_no_ex = min(predicted_no_ex, 10)
    command = [SPARK_SUBMIT_BASH, f"trial{file_size}mb{assigned_no_ex}e", args.input_file, str(assigned_no_ex)]
    subprocess.run(command, check=True)

    # read data from the file bash produced
    time = -1.0
    if os.path.exists(BASH_OUTPUT_FILENAME):
        with open(BASH_OUTPUT_FILENAME) as file:
            raw_time = file.read().strip()
            try:
                time = float(raw_time)
            except:
                print("file content wasnt expected, using {time}s")
    else:
        print(f"Warning: {BASH_OUTPUT_FILENAME} not found. Measured execution time will be set to -1.")

    with open(OUTPUT_CSV, "a") as file:
            writer = csv.writer(file)
            print(f"Logging: {TIMESTAMP}, {file_size}, {predicted_no_ex}, {predicted_ex_time}, {assigned_no_ex}, {time}")
            writer.writerow([TIMESTAMP, file_size, predicted_no_ex, predicted_ex_time, assigned_no_ex, time])

if __name__ == "__main__":
    main()