import pickle
import hashlib
import os
import threading
import mmh3
import xxhash
import sqlite3

from parser_params import get_params
from banco import Banco
from logger.log import debug, warn
from environment import init_env


#from . import CONEXAO_BANCO

# Opening database connection and creating select query to the database
# to populate DATA_DICTIONARY

# print(os.path.exists(".intpy"))
init_env()
g_argsp_m, g_argsp_M, g_argsp_s, g_argsp_no_cache, g_argsp_hash = get_params()

CONEXAO_BANCO = None
if(g_argsp_m != ['v01x']):
    CONEXAO_BANCO = Banco(os.path.join(".intpy", "intpy.db"))
DATA_DICTIONARY = {}
NEW_DATA_DICTIONARY = {}
FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()


def _save(file_name):
    CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file) VALUES (?)", (file_name,))


#Versão desenvolvida por causa do _save em salvarNovosDadosBanco para a v0.2.5.x e a v0.2.6.x, com o nome da função
#Testar se existe a sobrecarga
def _save_fun_name(file_name, fun_name):
    CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file, fun_name) VALUES (?, ?)", (file_name, fun_name))


def _get(id):
    return CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE cache_file = ?", (id,))


#Versão desenvolvida por causa do _get_fun_name, que diferente do _get, recebe o nome da função ao invés do id, serve para a v0.2.5.x e a v0.2.6.x, que tem o nome da função
def _get_fun_name(fun_name):
    return CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE fun_name = ?", (fun_name,))


def _remove(id):
    CONEXAO_BANCO.executarComandoSQLSemRetorno("DELETE FROM CACHE WHERE cache_file = ?;", (id,))


def _get_id(fun_args, fun_source):
    if g_argsp_hash[0] == 'md5':
        return hashlib.md5((str(fun_args) + fun_source).encode('utf')).hexdigest()
    elif g_argsp_hash[0] == 'murmur':
        return hex(mmh3.hash128((str(fun_args) + fun_source).encode('utf')))[2:]
    elif g_argsp_hash[0] == 'xxhash':
        return xxhash.xxh128_hexdigest((str(fun_args) + fun_source).encode('utf'))


def _get_file_name(id):
    return "{0}.{1}".format(id, "ipcache")


def _autofix(id):
    debug("starting autofix")
    debug("removing {0} from database".format(id))
    _remove(_get_file_name(id))
    debug("environment fixed")


def _deserialize(id):
    try:
        with open(".intpy/cache/{0}".format(_get_file_name(id)), 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError as e:
        warn("corrupt environment. Cache reference exists for a function in database but there is no file for it in cache folder.\
            Have you deleted cache folder?")
        _autofix(id)
        return None


def _serialize(return_value, file_name):
    with open(".intpy/cache/{0}".format(_get_file_name(file_name)), 'wb') as file:
        return pickle.dump(return_value, file, protocol=pickle.HIGHEST_PROTOCOL)


def _get_cache_data_v01x(id):
    global CONEXAO_BANCO
    CONEXAO_BANCO = Banco(os.path.join(".intpy", "intpy.db"))
    list_file_name = _get(_get_file_name(id))
    CONEXAO_BANCO.fecharConexao()
    return _deserialize(id) if len(list_file_name) == 1 else None


def _get_cache_data_v021x(id):
    #Nesta versão, DATA_DICTIONARY armazena os dados novos ainda não
    #persistidos no banco de dados
    if(id in DATA_DICTIONARY):
        return DATA_DICTIONARY[id]
    list_file_name = _get(_get_file_name(id))
    return _deserialize(id) if len(list_file_name) == 1 else None


def _get_cache_data_v022x(id):
    #Nesta versão, DATA_DICTIONARY armazena os dados novos ainda não
    #persistidos no banco de dados e os dados já persitidos no banco de dados
    if(id in DATA_DICTIONARY):
        return DATA_DICTIONARY[id]
    return None


def _get_cache_data_v023x(id):
    if(id in DATA_DICTIONARY):
        return DATA_DICTIONARY[id]    
    if(id in NEW_DATA_DICTIONARY):
        return NEW_DATA_DICTIONARY[id]
    return None


def _get_cache_data_v024x(id):
    with CACHED_DATA_DICTIONARY_SEMAPHORE:
        if(id in DATA_DICTIONARY):
            return DATA_DICTIONARY[id]
    if(id in NEW_DATA_DICTIONARY):
        return NEW_DATA_DICTIONARY[id]
    return None


def _get_cache_data_v025x(id, fun_name):
    if(fun_name in FUNCTIONS_ALREADY_SELECTED_FROM_DB):
        if(id in DATA_DICTIONARY):
            return DATA_DICTIONARY[id]
        if(id in NEW_DATA_DICTIONARY):
            #Nesta versão, os valores de NEW_DATA_DICTIONARY são a tupla
            #(retorno_da_funcao, nome_da_funcao)
            return NEW_DATA_DICTIONARY[id][0]
    else:
        list_file_names = _get_fun_name(fun_name)
        for file_name in list_file_names:
            file_name = file_name[0].replace(".ipcache", "")
            
            result = _deserialize(file_name)
            if(result is None):
                continue
            else:
                DATA_DICTIONARY[file_name] = result

        FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(fun_name)
        if(id in DATA_DICTIONARY):
            return DATA_DICTIONARY[id]
    return None


def _get_cache_data_v026x(id, fun_name):
    if(fun_name in FUNCTIONS_ALREADY_SELECTED_FROM_DB):
        with CACHED_DATA_DICTIONARY_SEMAPHORE:
            if(id in DATA_DICTIONARY):
                return DATA_DICTIONARY[id]
        if(id in NEW_DATA_DICTIONARY):
            #Nesta versão, os valores de NEW_DATA_DICTIONARY são a tupla
            #(retorno_da_funcao, nome_da_funcao)
            return NEW_DATA_DICTIONARY[id][0]
    else:
        FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(fun_name)        
        id_file_name = _get_file_name(id)
        list_file_names = _get_fun_name(fun_name)
        for file_name in list_file_names:
            if(file_name[0] == id_file_name):
                thread = threading.Thread(target=add_new_data_to_CACHED_DATA_DICTIONARY, args=(list_file_names,))
                thread.start()

                file_name = file_name[0].replace(".ipcache", "")
                return _deserialize(file_name)
        
        thread = threading.Thread(target=add_new_data_to_CACHED_DATA_DICTIONARY, args=(list_file_names,))
        thread.start()
    return None


#Comparável à versão v021x, mas com 2 dicionários
def _get_cache_data_v027x(id):
    if(id in DATA_DICTIONARY):
        return DATA_DICTIONARY[id]
    if(id in NEW_DATA_DICTIONARY):
        return NEW_DATA_DICTIONARY[id]
    
    list_file_name = _get(_get_file_name(id))
    result = _deserialize(id) if len(list_file_name) == 1 else None
    if(result is not None):
        DATA_DICTIONARY[id] = result
    return result



def _get_cache_data_v2dmp(id):
    if (id in DATA_DICTIONARY):
        return DATA_DICTIONARY[id]
    
    # list_file_name = _get(_get_file_name(id))
    # result = _deserialize(id) if len(list_file_name) == 1 else None
    # if(result is not None):
    #     DATA_DICTIONARY[id] = result
    # return result
    return None


def get_cache_data_v2dmp_storage(id):
    list_file_name = _get(_get_file_name(id))
    # print(f"{list_file_name=}")
    return _deserialize(id) if len(list_file_name) == 1 else None



# Aqui misturam as versões v0.2.1.x a v0.2.7.x e v01x
def get_cache_data(fun_name, fun_args, fun_source, argsp_v):
    id = _get_id(fun_args, fun_source)

    if(argsp_v == ['v01x']):
        ret_get_cache_data_v01x = _get_cache_data_v01x(id)
        return ret_get_cache_data_v01x
    elif(argsp_v == ['1d-ow'] or argsp_v == ['v021x']):
        ret_get_cache_data_v021x = _get_cache_data_v021x(id)
        return ret_get_cache_data_v021x
    elif(argsp_v == ['1d-ad'] or argsp_v == ['v022x']):
        ret_get_cache_data_v022x = _get_cache_data_v022x(id)
        return ret_get_cache_data_v022x
    elif(argsp_v == ['2d-ad'] or argsp_v == ['v023x']):
        ret_get_cache_data_v023x = _get_cache_data_v023x(id)
        return ret_get_cache_data_v023x
    elif(argsp_v == ['2d-ad-t'] or argsp_v == ['v024x']):
        ret_get_cache_data_v024x = _get_cache_data_v024x(id)
        return ret_get_cache_data_v024x
    elif(argsp_v == ['2d-ad-f'] or argsp_v == ['v025x']):
        ret_get_cache_data_v025x = _get_cache_data_v025x(id, fun_name)
        return ret_get_cache_data_v025x
    elif(argsp_v == ['2d-ad-ft'] or argsp_v == ['v026x']):
        ret_get_cache_data_v026x = _get_cache_data_v026x(id, fun_name)
        return ret_get_cache_data_v026x
    elif(argsp_v == ['2d-lz'] or argsp_v == ['v027x']):
        ret_get_cache_data_v027x = _get_cache_data_v027x(id)
        return ret_get_cache_data_v027x
    elif(argsp_v == ['2d-mp']):
        return _get_cache_data_v2dmp(id)



def add_new_data_to_CACHED_DATA_DICTIONARY(list_file_names):
    for file_name in list_file_names:
        file_name = file_name[0].replace(".ipcache", "")
        
        result = _deserialize(file_name)
        if(result is None):
            continue
        else:
            with CACHED_DATA_DICTIONARY_SEMAPHORE:
                DATA_DICTIONARY[file_name] = result


def create_entry_main_memory_cache(fun_args, fun_return, fun_source):
    id = _get_id(fun_args, fun_source)
    DATA_DICTIONARY[id] = fun_return


# Aqui misturam as versões v0.2.1.x a v0.2.7.x e v01x
def create_entry(fun_name, fun_args, fun_return, fun_source, argsp_v):
    id = _get_id(fun_args, fun_source)
    if argsp_v == ['v01x']:
        global CONEXAO_BANCO
        CONEXAO_BANCO = Banco(os.path.join(".intpy", "intpy.db"))
        debug("serializing return value from {0}".format(id))
        _serialize(fun_return, id)
        debug("inserting reference in database")
        _save(_get_file_name(id))
        CONEXAO_BANCO.salvarAlteracoes()
        CONEXAO_BANCO.fecharConexao()

    elif(argsp_v == ['1d-ow'] or argsp_v == ['v021x'] or
        argsp_v == ['1d-ad'] or argsp_v == ['v022x']):
        DATA_DICTIONARY[id] = fun_return
    elif(argsp_v == ['2d-ad'] or argsp_v == ['v023x'] or 
        argsp_v == ['2d-ad-t'] or argsp_v == ['v024x'] or
        argsp_v == ['2d-lz'] or argsp_v == ['v027x']):
        NEW_DATA_DICTIONARY[id] = fun_return
    elif(argsp_v == ['2d-ad-f'] or argsp_v == ['v025x'] or
        argsp_v == ['2d-ad-ft'] or argsp_v == ['v026x']):
        NEW_DATA_DICTIONARY[id] = (fun_return, fun_name)


def create_entry_v2(fun_name, fun_args, fun_return, fun_source, argsp_v):
    id = _get_id(fun_args, fun_source)
    db = Banco(os.path.join(".intpy", "intpy.db"))
    _serialize(fun_return, id)
    db.executarComandoSQLSemRetorno(f"INSERT OR IGNORE INTO CACHE(cache_file) VALUES ({_get_file_name(id)})")
    db.salvarAlteracoes()
    db.fecharConexao()


def salvarNovosDadosBancoV2DMP():
    # print(f"{DATA_DICTIONARY=}")
    for id in DATA_DICTIONARY:
        _serialize(DATA_DICTIONARY[id], id)
        file_name = _get_file_name(id)
        # _save(_get_file_name(id))
        bd = sqlite3.connect(".intpy/intpy.db")
        bd.execute("INSERT OR IGNORE INTO CACHE(cache_file) VALUES (?)", (file_name,))
        bd.commit()
        bd.close()



# Aqui misturam as versões v0.2.1.x a v0.2.7.x
def salvarNovosDadosBanco(argsp_v):
    if(argsp_v == ['1d-ow'] or argsp_v == ['v021x'] or
        argsp_v == ['1d-ad'] or argsp_v == ['v022x']):
        for id in DATA_DICTIONARY:
            debug("serializing return value from {0}".format(id))
            _serialize(DATA_DICTIONARY[id], id)
            debug("inserting reference in database")
            _save(_get_file_name(id))
    
    elif(argsp_v == ['2d-ad'] or argsp_v == ['v023x'] or
        argsp_v == ['2d-ad-t'] or argsp_v == ['v024x'] or
        argsp_v == ['2d-lz'] or argsp_v == ['v027x']):
        for id in NEW_DATA_DICTIONARY:
            debug("serializing return value from {0}".format(id))
            _serialize(NEW_DATA_DICTIONARY[id], id)
            debug("inserting reference in database")
            _save(_get_file_name(id))
    
    elif(argsp_v == ['2d-ad-f'] or argsp_v == ['v025x'] or
        argsp_v == ['2d-ad-ft'] or argsp_v == ['v026x']):
        for id in NEW_DATA_DICTIONARY:
            debug("serializing return value from {0}".format(id))
            _serialize(NEW_DATA_DICTIONARY[id][0], id)
            debug("inserting reference in database")
            _save_fun_name(_get_file_name(id), NEW_DATA_DICTIONARY[id][1])

    CONEXAO_BANCO.salvarAlteracoes()
    CONEXAO_BANCO.fecharConexao()
   

if(g_argsp_m == ['1d-ad'] or g_argsp_m == ['v022x']
    or g_argsp_m == ['2d-ad'] or g_argsp_m == ['v023x']):
    def _populate_cached_data_dictionary():
        list_of_ipcache_files = CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE")
        for ipcache_file in list_of_ipcache_files:
            ipcache_file = ipcache_file[0].replace(".ipcache", "")
            result = _deserialize(ipcache_file)
            if(result is None):
                continue
            else:
                DATA_DICTIONARY[ipcache_file] = result
    _populate_cached_data_dictionary()
elif(g_argsp_m == ['2d-ad-t'] or g_argsp_m == ['v024x']):
    def _populate_cached_data_dictionary():
        db_connection = Banco(os.path.join(".intpy", "intpy.db"))
        list_of_ipcache_files = db_connection.executarComandoSQLSelect("SELECT cache_file FROM CACHE")
        for ipcache_file in list_of_ipcache_files:
            ipcache_file = ipcache_file[0].replace(".ipcache", "")
            
            result = _deserialize(ipcache_file)
            if(result is None):
                continue
            else:
                with CACHED_DATA_DICTIONARY_SEMAPHORE:
                    DATA_DICTIONARY[ipcache_file] = result
        db_connection.fecharConexao()
    load_cached_data_dictionary_thread = threading.Thread(target=_populate_cached_data_dictionary)
    load_cached_data_dictionary_thread.start()
