import inspect
import time
import sys
import os
import signal
import logging
import multiprocessing

from functools import wraps

from parser_params import get_params
from environment import get_inter_cache_value
from logger.log import debug
from data_access import get_cache_data, create_entry, salvarNovosDadosBanco, create_entry_main_memory_cache, _get_id, get_cache_data_v2dmp_storage, salvarNovosDadosBancoV2DMP
from function_graph import create_experiment_function_graph, get_source_code_executed

logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs.txt", level=logging.DEBUG)

g_user_script_graph = None
EXECUTION_PROC = "execution_proc"
CACHE_PROC = "cache_proc"

g_argsp_m, g_argsp_M, g_argsp_s, g_argsp_no_cache, g_argsp_hash = get_params()
# print(f"{g_argsp_m=}")
# print(f"{g_argsp_no_cache=}")
# print(f"{g_argsp_hash=}")


def get_execution_params():
    
    v1 = g_argsp_m if type(g_argsp_m) != list else g_argsp_m[0]
    v2 = g_argsp_M if type(g_argsp_M) != list else g_argsp_M[0]
    v3 = g_argsp_s if type(g_argsp_s) != list else g_argsp_s[0]
    v4 = g_argsp_no_cache if type(g_argsp_no_cache) != list else g_argsp_no_cache[0]
    v5 = g_argsp_hash if type(g_argsp_hash) != list else g_argsp_hash[0]
    v6 = True # intra_cache
    v7 = get_inter_cache_value() # inter_cache

    return v1, v2, v3, v4, v5, v6, v7

def get_g_user_script_graph():
    return g_user_script_graph

if g_argsp_m == None and not g_argsp_no_cache:
    print("Error: enter the \"-h\" parameter on the command line after \"python script.py\" to see usage instructions")
    sys.exit()

if g_argsp_no_cache:
    #On the decorator "initialize_intpy", "user_script_path" is declared
    #to maintain compatibility
    def initialize_intpy(user_script_path):
        def decorator(f):
            def execution(*method_args, **method_kwargs):
                f(*method_args, **method_kwargs)
            return execution
        return decorator


    def deterministic(f):
        return f
else:
    # init_env()
    from data_access import get_cache_data, create_entry, salvarNovosDadosBanco
    from function_graph import create_experiment_function_graph, get_source_code_executed

    def _initialize_cache(user_script_path):
        # print("init graph")
        global g_user_script_graph
        res = create_experiment_function_graph(user_script_path)
        g_user_script_graph = res
        return res


    def initialize_intpy(user_script_path):
        def decorator(f):
            def execution(*method_args, **method_kwargs):
                _initialize_cache(user_script_path)
                f(*method_args, **method_kwargs)
                if g_argsp_m != ['v01x']:
                    _salvarCache()
            return execution
        return decorator


    def deterministic_v3(g_user_script_graph):
        def decorator(f):
            return _function_call_with_cache_lookup(f, g_user_script_graph)
        return decorator


    def deterministic_v2(g_user_script_graph):
        def decorator(f):
            return _function_call_no_cache_lookup(f, g_user_script_graph)
        return decorator
    

    def deterministic(f):
        return _method_call(f) if _is_method(f) else _function_call(f)


    def _get_cache(func, args):
        fun_source = get_source_code_executed(func, g_user_script_graph)
        return get_cache_data(func.__name__, args, fun_source, g_argsp_m)


    def _get_cache_v2(func, args, g_user_script_graph, g_argsp_m):
        fun_source = get_source_code_executed(func, g_user_script_graph)
        return get_cache_data(func.__name__, args, fun_source, g_argsp_m)
    

    def get_cache_2d_mp_storage(func, args, g_user_script_graph):
        # print(f"{g_user_script_graph=}")
        # print(f"g_user_script_graph == None : {g_user_script_graph==None}")
        # print(f"(READ) g_user_script_graph : {g_user_script_graph.__hash__}")
        # logger.debug(f"[CACHE_PROC] func = {func.__name__} / args: {args}")
        fun_source = get_source_code_executed(func, g_user_script_graph)
        id = _get_id(args, fun_source)
        # logger.debug(f"[CACHE_PROC] cache id: {id} / func = {func.__name__} / args = {args}")
        return get_cache_data_v2dmp_storage(id)



    def _cache_exists(cache):
        return cache is not None


    def _cache_data(func, fun_args, fun_return, elapsed_time):
        debug("starting caching data for {0}({1})".format(func.__name__, fun_args))
        # print(f"[_cache_data] : {g_user_script_graph}")
        start = time.perf_counter()
        fun_source = get_source_code_executed(func, g_user_script_graph)
        create_entry(func.__name__, fun_args, fun_return, fun_source, g_argsp_m)
        end = time.perf_counter()
        debug("caching {0} took {1}".format(func.__name__, end - start))

    def _cache_data_v2(func, fun_args, fun_return, g_user_script_graph):
        # print(f"g_user_script_graph == None : {g_user_script_graph==None}")
        # print(f"(SALVAR) g_user_script_graph : {g_user_script_graph.__hash__}")
        debug("starting caching data for {0}({1})".format(func.__name__, fun_args))
        start = time.perf_counter()
        # logger.debug(f"[EXECUTION PROC] function: {func.__name__} / args: {fun_args}")
        fun_source = get_source_code_executed(func, g_user_script_graph)
        create_entry_main_memory_cache(fun_args, fun_return, fun_source)
        end = time.perf_counter()
        debug("caching {0} took {1}".format(func.__name__, end - start))


    def _execute_func(f, self, *method_args, **method_kwargs):
        start = time.perf_counter()
        result_value = f(self, *method_args, **method_kwargs) if self is not None else f(*method_args, **method_kwargs)
        end = time.perf_counter()

        elapsed_time = end - start

        debug("{0} took {1} to run".format(f.__name__, elapsed_time))

        return result_value, elapsed_time


    def _method_call(f):
        @wraps(f)
        def wrapper(self, *method_args, **method_kwargs):
            debug("calling {0}".format(f.__name__))
            c = _get_cache(f, method_args)
            if not _cache_exists(c):
                debug("cache miss for {0}({1})".format(f.__name__, *method_args))
                return_value, elapsed_time = _execute_func(f, self, *method_args, **method_kwargs)
                _cache_data(f, method_args, return_value, elapsed_time)
                return return_value
            else:
                debug("cache hit for {0}({1})".format(f.__name__, *method_args))
                return c

        return wrapper


    def _function_call(f):
        @wraps(f)
        def wrapper(*method_args, **method_kwargs):
            debug("calling {0}".format(f.__name__))
            c = _get_cache(f, method_args)
            if not _cache_exists(c):
                debug("cache miss for {0}({1})".format(f.__name__, *method_args))
                return_value, elapsed_time = _execute_func(f, *method_args, **method_kwargs)
                _cache_data(f, method_args, return_value, elapsed_time)
                return return_value
            else:
                debug("cache hit for {0}({1})".format(f.__name__, *method_args))
                return c

        return wrapper


    def _function_call_with_cache_lookup(f, g_user_script_graph):
        """
        dada uma funcao e argumentos, confere se existe resultado em cache. Se existir, retorna o resultado. Caso contrario executa a função
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            cached_res = _get_cache_v2(f, args, g_user_script_graph, ['2d-mp'])
            result = None

            if cached_res == None:
                # logger.debug(f"[EXECUTION_PROC] cache miss: function {f.__name__} / args: {args}")
                result, _ = _execute_func(f, *args, **kwargs)
                _cache_data_v2(f, args, result, g_user_script_graph)
            else:
                # logger.debug(f"[EXECUTION_PROC] cache hit: function {f.__name__} / args: {args}")
                result = cached_res
            
            return result

        return wrapper
    

    def _function_call_no_cache_lookup(f, g_user_script_graph):
        """
        executa a funcao, sem consultar dados no cache, mas salva os resultados em um cache que serão posteriorment salvos em banco
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            result, _ = _execute_func(f, *args, **kwargs)
            _cache_data_v2(f, args, result, g_user_script_graph)
            return result

        return wrapper


    def function_executer(shared_dict, barrier, proc_name, function, *args, **kwargs):
        pid = os.getpid()
        shared_dict["procs"] = shared_dict["procs"] + [pid]
        
        barrier.wait()
        print(f"begin function {function.__name__} / pid = {pid}")
        res = function(*args, **kwargs)
        print(f"end function {function.__name__}")

        print(f"{proc_name} terminou")

        if (res != None and proc_name == "p2") or proc_name == "p1":
            shared_dict["res"] = res
            shared_dict["win_func"] = function.__name__

            for p in shared_dict["procs"]:
                if p != pid:
                    os.kill(p, signal.SIGTERM)

        return res

    # obs
    def _is_method(f):
        args = inspect.getfullargspec(f).args
        return bool(args and args[0] == 'self')


    def executeFunctionAndSave(function, *args):
        res = function(*args)
        salvarNovosDadosBancoV2DMP()
        return res



    def _salvarCache():
        salvarNovosDadosBanco(g_argsp_m)



    def function_executer(shared_dict, barrier, proc_name, function, *args, **kwargs):
        pid = os.getpid()
        shared_dict["procs"] = shared_dict["procs"] + [pid]
        
        barrier.wait()
        # print(f"begin function {function.__name__} / pid = {pid}\n")
        res = function(*args, **kwargs)
        # print(f"end function {function.__name__}\n")

        # print(f"{proc_name} terminou\n")

        # if proc_name == "p1":
        #     print("execucao normal terminou\n")
        # else:
        #     print("busca em cache terminou\n")

        if (res == None and proc_name == CACHE_PROC):
            # print("cache_lookup_proc terminou - nenhum resultado em cache")
            shared_dict["procs"] = list(filter(lambda x : x != pid, shared_dict["procs"]))

        if (res != None and proc_name == CACHE_PROC) or proc_name == EXECUTION_PROC:
            # print("achou res valido\n")
            shared_dict["res"] = res
            shared_dict["win_proc"] = proc_name

            for p in shared_dict["procs"]:
                if p != pid:
                    os.kill(p, signal.SIGTERM)
                    # print(f"matou proc {p}")

        return res


    def execute_experiment(shared_dict, barrier, function, *args):
        
        exec_proc_args = (function, *args)
        # print(f"{exec_proc_args=}")
        p1 = multiprocessing.Process(target=function_executer, args=(shared_dict, barrier, EXECUTION_PROC, executeFunctionAndSave, *exec_proc_args))

        cache_function_args = (function, args, get_g_user_script_graph())
        # print(f"{cache_function_args=}")
        p2 = multiprocessing.Process(target=function_executer, args=(shared_dict, barrier, CACHE_PROC, get_cache_2d_mp_storage, *cache_function_args))

        p1.start()
        p2.start()

        p1.join()
        p2.join()

        # print(f"{shared_dict=}")

        return shared_dict
