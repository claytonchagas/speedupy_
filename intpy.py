import inspect
import time
import sys, os, signal

from functools import wraps

from parser_params import get_params
from environment import init_env
from logger.log import debug

import multiprocessing

g_argsp_m, g_argsp_M, g_argsp_s, g_argsp_no_cache, g_argsp_hash, g_argsp_mp  = get_params()

print(g_argsp_m)
print(g_argsp_no_cache)
print(g_argsp_hash)
print(g_argsp_mp)

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
    init_env()
    from data_access import get_cache_data, create_entry, salvarNovosDadosBanco
    from function_graph import create_experiment_function_graph, get_source_code_executed

    g_user_script_graph = None
    def _initialize_cache(user_script_path):
        global g_user_script_graph
        g_user_script_graph = create_experiment_function_graph(user_script_path)

    def initialize_intpy(user_script_path):
        def decorator(f):
            def execution(*method_args, **method_kwargs):
                _initialize_cache(user_script_path)
                f(*method_args, **method_kwargs)
                if g_argsp_m != ['v01x']:
                    _salvarCache()
            return execution
        return decorator


    def deterministic(f):
        global g_argsp_mp
        if not g_argsp_mp:
            return _method_call(f) if _is_method(f) else _function_call(f)
        else:
            # print("como tá o argmp",g_argsp_mp)
            # g_argsp_mp = False
            @wraps(f)
            def wrapper(*args, **kwargs):
                manager = multiprocessing.Manager()
                shared_dict = manager.dict()
                shared_dict["procs"] = []
                barrier = multiprocessing.Barrier(2)
                def run_func(func,target_func, shared_dict, barrier, is_principal=False):
                    pid = os.getpid()
                    shared_dict["procs"] = shared_dict["procs"] + [pid]
                    
                    barrier.wait()
                    
                    res = target_func(*args, **kwargs) if is_principal else target_func(func)
                    
                    shared_dict["res"] = res
                    shared_dict["winner"] = target_func.__name__

                    for p in shared_dict["procs"]:
                        if p != pid:
                            os.kill(p, signal.SIGTERM)
                    # return res
                # Criando processos
                process_a = multiprocessing.Process(target=run_func, args=(f,f, shared_dict, barrier, True))
                if _is_method(f):
                    process_b = multiprocessing.Process(target=run_func, args=(f,_method_call, shared_dict, barrier, False))
                else:
                    process_b = multiprocessing.Process(target=run_func, args=(f,_function_call, shared_dict, barrier, False))
                
                process_a.start()
                process_b.start()

                process_a.join()
                process_b.join()        
                
                # print(f"tipo do resultado é {type(shared_dict["res"])}")
                return shared_dict["res"]
            return wrapper


    def _get_cache(func, args):
        fun_source = get_source_code_executed(func, g_user_script_graph)
        return get_cache_data(func.__name__, args, fun_source, g_argsp_m)


    def _cache_exists(cache):
        return cache is not None


    def _cache_data(func, fun_args, fun_return, elapsed_time):
        debug("starting caching data for {0}({1})".format(func.__name__, fun_args))
        start = time.perf_counter()
        fun_source = get_source_code_executed(func, g_user_script_graph)
        create_entry(func.__name__, fun_args, fun_return, fun_source, g_argsp_m)
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
        time.sleep(1)
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

    # obs
    def _is_method(f):
        args = inspect.getfullargspec(f).args
        return bool(args and args[0] == 'self')


    def _salvarCache():
        salvarNovosDadosBanco(g_argsp_m)

    def run_multiprocess(f_call):
        def decorator(func):
            @wraps(func)
            def wrapper():
                def run(func, queue, barrier):
                    barrier.wait()  # Aguarda todas as funções estarem prontas para iniciar
                    func()
                    queue.put(func.__name__)  # Envia o nome da função que terminou
                
                queue = multiprocessing.Queue()
                barrier = multiprocessing.Barrier(2)  # Define uma barreira para sincronização
                
                p1 = multiprocessing.Process(target=run, args=(func, queue, barrier))
                p2 = multiprocessing.Process(target=run, args=(f_call(func), queue, barrier))
                
                p1.start()
                p2.start()
                
                winner = queue.get()  # Espera a primeira função terminar
                print(f"A função '{winner}' terminou primeiro.")
                
                # Finaliza os processos
                p1.terminate()
                p2.terminate()
                
                p1.join()
                p2.join()
            
            return wrapper
        return decorator
    
