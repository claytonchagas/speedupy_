import math
import concurrent.futures
import time
import sys
import logging

filename = "multithreading_test\\primes\\primes_multithreaded.log"

logging.basicConfig(filename=filename,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


# rodar com: C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python313\\python3.13t multithreading_test\\primes\\primes_multithreaded.py




def is_prime(n):

    if (n % 2) == 0:
        return False

    for i in range(3, int(math.sqrt(n))+1, 2):
        if (n % i) == 0:
            return False
    return True


def count_primes(start, stop, step):
    primes = 0
    for i in range(start, stop, step):
        if (is_prime(i)) == True:
            primes += 1
    return primes


def count_primes_multithreaded(n, num_threads=4):
    if n < 2:
        return 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []

        for thread_num in range(num_threads):
            start = 2 + thread_num
            step = num_threads
            # print(f"t = {thread_num} / {list(range(start, n, step))}")
            futures.append(executor.submit(count_primes, start, n, step))

        concurrent.futures.wait(futures)

    return sum([i.result() for i in futures]) + 1 # +1 because two is prime


print(f"argv = {sys.argv}")

n = int(sys.argv[1])
num_threads = int(sys.argv[2])
start = time.perf_counter()
res = count_primes_multithreaded(n, num_threads)
end = time.perf_counter()
# time_seconds = "{:e}".format(end-start)
time_seconds = f"{end-start:.20f}"

# logging.info(f"GIL enabled: {sys._is_gil_enabled()}")
py_version = sys.version.split(" ")[0]

logging.info(f"python version: {py_version}")
logging.info(f"num_threads: {num_threads}")
logging.info(f"function: {count_primes_multithreaded.__name__} / input = {n} / result = {res}")
logging.info(f"time = {time_seconds} seconds")
logging.info("#######################################")

# print(f"GIL enabled: {sys._is_gil_enabled()}")
print(f"python version: {py_version}")
print(f"num_threads: {num_threads}")
print(f"function: {count_primes_multithreaded.__name__} / input = {n} / result = {res}")
print(f"time = {time_seconds} seconds")
print("#######################################")
