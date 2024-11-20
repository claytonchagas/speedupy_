import time
import sys
import multiprocessing
import os
import cProfile
import pstats

from intpy import deterministic_v2, deterministic_v3, _initialize_cache, get_g_user_script_graph, get_execution_params, execute_experiment
# import pandas as pd
from util import add_row_to_dataFrame, iterable_to_csv_row, create_csv_file_if_not_exists

# @deterministic_v2(_initialize_cache(__file__))
@deterministic_v3(_initialize_cache(__file__))
def fib(n):
    if n < 2:
        return n
    else:
        return fib(n-1) + fib(n-2)


def main(shared_dict, barrier):
    n = int(sys.argv[1])
    
    start = time.perf_counter()
    data = execute_experiment(shared_dict, barrier, fib, n)
    end = time.perf_counter()
    
    total_time = round(end-start, 5)
    # print(data)
    # print(f"{total_time=}")
    

    df_name = "results.csv"
    columns = ["filename", "function_name", "n", "time", "memory", "storage", "marshaling", "no_cache", "hash", "intra_cache", "inter_cache"]
    create_csv_file_if_not_exists(df_name, columns)

    row = (os.path.basename(__file__), fib.__name__, n, total_time, *get_execution_params())
    row_str = iterable_to_csv_row(row)

    with open(df_name, "a") as f:
        f.write(row_str)

    return data


if __name__ == '__main__':

    manager = multiprocessing.Manager()
    barrier = multiprocessing.Barrier(2)
    shared_dict = manager.dict()
    shared_dict["procs"] = []

    main(shared_dict, barrier)

    # uso para profiling
    # with cProfile.Profile() as pr:
    #     main(shared_dict, barrier)
    
    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # # stats.print_stats()
    # stats.dump_stats("teste_multiprocessing.prof")
