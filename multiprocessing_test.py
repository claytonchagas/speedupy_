import multiprocessing
import time
import os
import signal


def fooA(n):
    time.sleep(10)
    return 2*n


def fooB(n):
    time.sleep(8)
    return 8*n


def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)


def fib_cache(n):
    print("simulating getting cache result...")
    time.sleep(2)
    return n*10


def function_executer(shared_dict, barrier, function, *args, **kwargs):
    pid = os.getpid()
    shared_dict["procs"] = shared_dict["procs"] + [pid]
    
    barrier.wait()
    print(f"begin function {function.__name__} / pid = {pid}")
    res = function(*args, **kwargs)
    print(f"end function {function.__name__}")

    shared_dict["res"] = res
    shared_dict["win_func"] = function.__name__

    for p in shared_dict["procs"]:
        if p != pid:
            os.kill(p, signal.SIGTERM)

    return res



if __name__ == "__main__":
    processes = []
    manager = multiprocessing.Manager()
    barrier = multiprocessing.Barrier(2)
    shared_dict = manager.dict()
    shared_dict["procs"] = []
    # run = manager.Event()
    # run.set()

    # p1 = multiprocessing.Process(target=fooA, args=(5, shared_dict))
    # p2 = multiprocessing.Process(target=fooB, args=(5, shared_dict))

    
    # p1 = multiprocessing.Process(target=function_executer, args=(shared_dict, fooA, 5))
    # p2 = multiprocessing.Process(target=function_executer, args=(shared_dict, fooB, 5))

    # caso que processamento normal eh mais rapido
    # p1 = multiprocessing.Process(target=function_executer, args=(shared_dict, barrier, fib, 5))
    # p2 = multiprocessing.Process(target=function_executer, args=(shared_dict, barrier, fib_cache, 5))

    # caso que recuperar da cache normal eh mais rapido
    p1 = multiprocessing.Process(target=function_executer, args=(shared_dict, barrier, fib, 50))
    p2 = multiprocessing.Process(target=function_executer, args=(shared_dict, barrier, fib_cache, 50))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print(shared_dict)

    