import time
import sys
import multiprocessing

from intpy import deterministic_v2, deterministic_v3, _initialize_cache, get_g_user_script_graph
from intpyClass import Speedupy 

# @deterministic_v2(_initialize_cache(__file__))
@deterministic_v3(_initialize_cache(__file__))
def fib(n):
    if n < 2:
        return n
    else:
        return fib(n-1) + fib(n-2)


def main(n):
    return fib(n)


if __name__ == '__main__':

    manager = multiprocessing.Manager()
    barrier = multiprocessing.Barrier(2)
    shared_dict = manager.dict()
    shared_dict["procs"] = []

    speedupy = Speedupy(get_g_user_script_graph(), shared_dict, barrier)
    n = int(sys.argv[1])
    
    start = time.perf_counter()
    data = speedupy.execute_experiment(fib, n)
    end = time.perf_counter()

    print(f"total time = {end-start}")
