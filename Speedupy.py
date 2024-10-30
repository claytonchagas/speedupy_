import sys
import multiprocessing
import os
import signal


from DataAccess import DataAccess
from parser_params import get_params
from function_graph import create_experiment_function_graph, get_source_code_executed

class Speedupy:
    def __init__(self, user_script_path, shared_dict, barrier) -> None:

        self.g_argsp_m = None
        self.g_argsp_M = None
        self.g_argsp_s = None
        self.g_argsp_no_cache = None
        self.g_argsp_hash = None
    
        self.init_params()

        self.dataAccess = DataAccess()
        self.shared_dict = shared_dict
        self.barrier = barrier

        self.g_user_script_graph = create_experiment_function_graph(user_script_path)
        self.function = None

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


    def _get_cache(self, func, args):
        fun_source = get_source_code_executed(func, self.g_user_script_graph)
        return self.dataAccess.get_cache_data(func.__name__, args, fun_source, self.g_argsp_m)

    
    def function_executer(self, proc_name, function, *args, **kwargs):
        pid = os.getpid()
        self.shared_dict["procs"] = self.shared_dict["procs"] + [pid]
        
        self.barrier.wait()
        print(f"begin function {function.__name__} / pid = {pid}\n")
        res = function(*args, **kwargs)
        print(f"end function {function.__name__}\n")

        # print(f"{proc_name} terminou\n")

        # if proc_name == "p1":
        #     print("execucao normal terminou\n")
        # else:
        #     print("busca em cache terminou\n")

        if (res != None and proc_name == "p2") or proc_name == "p1":
            # print("achou res valido\n")
            self.shared_dict["res"] = res
            self.shared_dict["win_func"] = function.__name__

            for p in self.shared_dict["procs"]:
                if p != pid:
                    os.kill(p, signal.SIGTERM)
                    # print(f"matou proc {p}")

        return res


    def select_experiment(self, function):
        self.function = function

    
    def get_cached_data_wrapper(self, *args):
        return self._get_cache(self.function, args)


    def execute_experiment(self, function, *args):

        self.select_experiment(function)
        
        p1 = multiprocessing.Process(target=self.function_executer, args=("p1", self.function, *args))
        p2 = multiprocessing.Process(target=self.function_executer, args=("p2", self.get_cached_data_wrapper, *args))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        print(self.shared_dict)

        return self.shared_dict

    