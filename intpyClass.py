import sys
import multiprocessing
import os
import signal
import time

from DataAccess import DataAccess
from parser_params import get_params
from intpy import _initialize_cache, _get_cache_v2, executeFunctionAndSave, get_cache_2d_mp_storage

EXECUTION_PROC = "execution_proc"
CACHE_PROC = "cache_proc"

class Speedupy:
    def __init__(self, user_script_path, shared_dict, barrier) -> None:

        self.g_argsp_m = None
        self.g_argsp_M = None
        self.g_argsp_s = None
        self.g_argsp_no_cache = None
        self.g_argsp_hash = None
    
        self.init_params()
        self.g_user_script_graph = _initialize_cache(user_script_path)

        self.dataAccess = DataAccess()
        self.shared_dict = shared_dict
        self.barrier = barrier


    def init_params(self) -> None:
        g_argsp_m, g_argsp_M, g_argsp_s, g_argsp_no_cache, g_argsp_hash = get_params()

        if g_argsp_m == None and not g_argsp_no_cache:
            print("Error: enter the \"-h\" parameter on the command line after \"python script.py\" to see usage instructions")
            sys.exit()

        self.g_argsp_m = g_argsp_m
        self.g_argsp_M = g_argsp_M
        self.g_argsp_s = g_argsp_s
        self.g_argsp_no_cache = g_argsp_no_cache
        self.g_argsp_hash = g_argsp_hash


    @staticmethod
    def function_executer(shared_dict, barrier, proc_name, function, *args, **kwargs):
        pid = os.getpid()
        shared_dict["procs"] = shared_dict["procs"] + [pid]
        
        barrier.wait()
        print(f"begin function {function.__name__} / pid = {pid}\n")
        res = function(*args, **kwargs)
        print(f"end function {function.__name__}\n")

        # print(f"{proc_name} terminou\n")

        # if proc_name == "p1":
        #     print("execucao normal terminou\n")
        # else:
        #     print("busca em cache terminou\n")

        if (res == None and proc_name == CACHE_PROC):
            print("cache_lookup_proc terminou - nenhum resultado em cache")
            shared_dict["procs"] = list(filter(lambda x : x != pid, shared_dict["procs"]))

        if (res != None and proc_name == CACHE_PROC) or proc_name == EXECUTION_PROC:
            # print("achou res valido\n")
            shared_dict["res"] = res
            shared_dict["win_proc"] = proc_name

            for p in shared_dict["procs"]:
                if p != pid:
                    os.kill(p, signal.SIGTERM)
                    print(f"matou proc {p}")

        return res


    def execute_experiment(self, function, *args):
        
        exec_proc_args = (function, *args)
        print(f"{exec_proc_args=}")
        p1 = multiprocessing.Process(target=self.function_executer, args=(self.shared_dict, self.barrier, EXECUTION_PROC, executeFunctionAndSave, *exec_proc_args))

        cache_function_args = (function, *args, self.g_user_script_graph)
        # print(f"{cache_function_args=}")
        p2 = multiprocessing.Process(target=self.function_executer, args=(self.shared_dict, self.barrier, CACHE_PROC, get_cache_2d_mp_storage, *cache_function_args))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        print(self.shared_dict)

        return self.shared_dict


