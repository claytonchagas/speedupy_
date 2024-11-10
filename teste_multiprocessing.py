import time
import sys
import multiprocessing

from intpy import deterministic_v2, _initialize_cache
from intpyClass import Speedupy 

graph = _initialize_cache(__file__)

# grafo ta como None
# @deterministic_v2(graph)
def fib(n):
    if n < 2:
        return n
    else:
        return fib(n-1) + fib(n-2)


fib = deterministic_v2(graph)(fib)


def main(n):
    return fib(n)


if __name__ == '__main__':

    manager = multiprocessing.Manager()
    barrier = multiprocessing.Barrier(2)
    shared_dict = manager.dict()
    shared_dict["procs"] = []

    speedupy = Speedupy(__file__, shared_dict, barrier)
    n = int(sys.argv[1])
    
    start = time.perf_counter()
    data = speedupy.execute_experiment(fib, n)
    end = time.perf_counter()

    print(f"total time = {end-start}")
