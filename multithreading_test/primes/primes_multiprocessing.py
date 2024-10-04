import math
import sys
import time
import multiprocessing
import logging
import os


def is_prime(n):

    if (n % 2) == 0:
        return False

    for i in range(3, int(math.sqrt(n))+1, 2):
        if (n % i) == 0:
            return False
    return True

def count_primes(start, n, step):
    if n < 2:
        return 0

    primes = 0

    for i in range(start, n, step):
        if (is_prime(i)) == True:
            primes += 1

    return primes


def count_primes_multiprocessing(shared_dict, n, proc_num, num_procs):
    start = 2 + proc_num
    step = num_procs
    primes_count = count_primes(start, n, step)
    shared_dict["primes"] = shared_dict["primes"] + primes_count



if __name__ == "__main__":

    filename = f"{__file__.split(".")[0]}.log"

    logging.basicConfig(filename=filename,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

    n = int(sys.argv[1])
    num_procs = int(sys.argv[2])
    manager = multiprocessing.Manager()
    shared_dict = manager.dict()
    shared_dict["primes"] = 0

    processes = []

    start = time.perf_counter()

    for i in range(num_procs):
        p = multiprocessing.Process(target=count_primes_multiprocessing, args=(shared_dict, n, i, num_procs))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    end = time.perf_counter()
    time_seconds = f"{end-start:.20f}"
    res = shared_dict["primes"] + 1

        
    logging.info(f"GIL enabled: {sys._is_gil_enabled()}")
    logging.info(f"num_procs: {num_procs}")
    logging.info(f"function: {count_primes_multiprocessing.__name__} / input = {n} / result = {res}")
    logging.info(f"time = {time_seconds} seconds")
    logging.info("#######################################")

    print(f"GIL enabled: {sys._is_gil_enabled()}")
    print(f"num_procs: {num_procs}")
    print(f"function: {count_primes_multiprocessing.__name__} / input = {n} / result = {res}")
    print(f"time = {time_seconds} seconds")
    print("#######################################")