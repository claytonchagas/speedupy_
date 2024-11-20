import time
import sys
import os

from intpy import deterministic,initialize_intpy, get_execution_params
from util import create_csv_file_if_not_exists, iterable_to_csv_row

@deterministic
def fib(n):
    if n < 2:
        return n
    else:
        return fib(n-1) + fib(n-2)

@initialize_intpy(__file__)
def main(n):
    fib(n)


if __name__ =='__main__':
    n = int(sys.argv[1])
    start = time.perf_counter()
    main(n)
    end = time.perf_counter()
    total_time = round(end-start, 5)
    # print(f"{total_time=}")

    df_name = "results.csv"
    columns = ["filename", "function_name", "n", "time", "memory", "storage", "marshaling", "no_cache", "hash", "intra_cache", "inter_cache"]
    create_csv_file_if_not_exists(df_name, columns)

    row = (os.path.basename(__file__), fib.__name__, n, total_time, *get_execution_params())
    row_str = iterable_to_csv_row(row)

    with open(df_name, "a") as f:
        f.write(row_str)