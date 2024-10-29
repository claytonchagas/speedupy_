import math
import time
import sys
import logging

filename = "multithreading_test\\primes\\primes.log"

logging.basicConfig(filename=filename,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


def is_prime(n):

    if (n % 2) == 0:
        return False

    for i in range(3, int(math.sqrt(n))+1, 2):
        if (n % i) == 0:
            return False
    return True

def count_primes(n):
    if n < 2:
        return 0

    primes = 1 # 2 eh primo

    for i in range(3, n+1):
        if (is_prime(i)) == True:
            # print(f"{i} is prime")
            primes += 1

    return primes



# print(f"argv = {sys.argv}")

n = int(sys.argv[1])
start = time.perf_counter()
res = count_primes(n)
end = time.perf_counter()
time_seconds = end-start
# time_seconds = "{:e}".format(end-start) # scientific notation
time_seconds = f"{end-start:.20f}"

# logging.info(f"GIL enabled: {sys._is_gil_enabled()}") # so existe a funcao sys._is_gil_enabled() no python 3.13
py_version = sys.version.split(" ")[0]

logging.info(f"python version: {py_version}")
logging.info(f"num_threads: 1")
logging.info(f"function: {count_primes.__name__} / input = {n} / result = {res}")
logging.info(f"time = {time_seconds} seconds")
logging.info("#######################################")

# print(f"GIL enabled: {sys._is_gil_enabled()}")
print(f"python version: {py_version}")
print(f"num_threads: 1")
print(f"function: {count_primes.__name__} / input = {n} / result = {res}")
print(f"time = {time_seconds} seconds")
print("#######################################")
