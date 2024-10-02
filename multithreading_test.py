import time
from threading import Thread
from multiprocessing import Process
import sys
import logging

filename = "multithreading_test.log"

logging.basicConfig(filename=filename,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


COUNT = 500000000

def countdown(n):
    while n>0:
        n -= 1


# CASO 1: programa sequencial
# rodar com: python multithreading.py

# start = time.perf_counter()
# countdown(COUNT)
# end = time.perf_counter()

# logging.info(f"GIL enbaled: {sys._is_gil_enabled()}")
# logging.info(f"Time taken in seconds -' {end - start}")
# logging.info("########################################")

# print(f"GIL enbaled: {sys._is_gil_enabled()}")
# print('Time taken in seconds -', end - start)
# print("########################################")

# ======================================================

# CASO 2: programa com multithreading sem gil
# obs rodar com o interpretador: python3.13t
# ex: %PATH_PYTHON_313%\\python3.13t multithreading_test.py

# t1 = Thread(target=countdown, args=(COUNT//2,))
# t2 = Thread(target=countdown, args=(COUNT//2,))

# start = time.perf_counter()
# t1.start()
# t2.start()
# t1.join()
# t2.join()
# end = time.perf_counter()

# logging.info(f"GIL enbaled: {sys._is_gil_enabled()}")
# logging.info(f"Time taken in seconds -' {end - start}")
# logging.info("########################################")

# print(f"GIL enbaled: {sys._is_gil_enabled()}")
# print('Time taken in seconds -', end - start)
# print("########################################")


# ======================================================

# CASO 3: multiprocessamento com versão python COM GIL
# rodar com: python multithreading.py

if __name__ == "__main__":

    p1 = Process(target=countdown, args=(COUNT//2,))
    p2 = Process(target=countdown, args=(COUNT//2,))

    start = time.perf_counter()
    p1.start()
    p2.start()

    p1.join()
    p2.join()

    end = time.perf_counter()

    logging.info("multiprocessing test")
    logging.info(f"GIL enbaled: {sys._is_gil_enabled()}")
    logging.info(f"Time taken in seconds - {end - start}")
    logging.info("########################################")

    print("multiprocessing test")
    print(f"GIL enbaled: {sys._is_gil_enabled()}")
    print(f"Time taken in seconds - {end - start}")
    print("########################################")