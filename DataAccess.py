import pickle
import hashlib
import os
import threading
import mmh3
import xxhash

from parser_params import get_params
from environment import init_env
from banco import Banco
from logger.log import debug, warn

class DataAccess:

    def __init__(self) -> None:

        init_env()

        self.g_argsp_m = None
        self.g_argsp_M = None
        self.g_argsp_s = None
        self.g_argsp_no_cache = None
        self.g_argsp_hash = None

        self.init_params()

        self.CONEXAO_BANCO = Banco(os.path.join(".intpy", "intpy.db"))
        self.DATA_DICTIONARY = {}
        self.NEW_DATA_DICTIONARY = {}
        self.FUNCTIONS_ALREADY_SELECTED_FROM_DB = []
        self.CACHED_DATA_DICTIONARY_SEMAPHORE = threading.Semaphore()

        
        if(self.g_argsp_m == ['1d-ad'] or self.g_argsp_m == ['v022x']
            or self.g_argsp_m == ['2d-ad'] or self.g_argsp_m == ['v023x']):
            def _populate_cached_data_dictionary():
                list_of_ipcache_files = self.CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE")
                for ipcache_file in list_of_ipcache_files:
                    ipcache_file = ipcache_file[0].replace(".ipcache", "")
                    result = self._deserialize(ipcache_file)
                    if(result is None):
                        continue
                    else:
                        self.DATA_DICTIONARY[ipcache_file] = result
            _populate_cached_data_dictionary()
        elif(self.g_argsp_m == ['2d-ad-t'] or self.g_argsp_m == ['v024x']):
            def _populate_cached_data_dictionary():
                db_connection = Banco(os.path.join(".intpy", "intpy.db"))
                list_of_ipcache_files = db_connection.executarComandoSQLSelect("SELECT cache_file FROM CACHE")
                for ipcache_file in list_of_ipcache_files:
                    ipcache_file = ipcache_file[0].replace(".ipcache", "")
                    
                    result = self._deserialize(ipcache_file)
                    if(result is None):
                        continue
                    else:
                        with self.CACHED_DATA_DICTIONARY_SEMAPHORE:
                            self.DATA_DICTIONARY[ipcache_file] = result
                db_connection.fecharConexao()
            load_cached_data_dictionary_thread = threading.Thread(target=_populate_cached_data_dictionary)
            load_cached_data_dictionary_thread.start()


    def init_params(self) -> None:
        g_argsp_m, g_argsp_M, g_argsp_s, g_argsp_no_cache, g_argsp_hash = get_params()

        self.g_argsp_m = g_argsp_m
        self.g_argsp_M = g_argsp_M
        self.g_argsp_s = g_argsp_s
        self.g_argsp_no_cache = g_argsp_no_cache
        self.g_argsp_hash = g_argsp_hash


    def _save(self, file_name):

        if self.CONEXAO_BANCO.isConnOpen is False:
            self.CONEXAO_BANCO.abrirConexao()

        self.CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file) VALUES (?)", (file_name,))

        self.CONEXAO_BANCO.salvarAlteracoes()
        self.CONEXAO_BANCO.fecharConexao()


    #Versão desenvolvida por causa do _save em salvarNovosDadosBanco para a v0.2.5.x e a v0.2.6.x, com o nome da função
    #Testar se existe a sobrecarga
    def _save_fun_name(self, file_name, fun_name):

        if self.CONEXAO_BANCO.isConnOpen is False:
            self.CONEXAO_BANCO.abrirConexao()
        
        self.CONEXAO_BANCO.executarComandoSQLSemRetorno("INSERT OR IGNORE INTO CACHE(cache_file, fun_name) VALUES (?, ?)", (file_name, fun_name))
        
        self.CONEXAO_BANCO.salvarAlteracoes()
        self.CONEXAO_BANCO.fecharConexao()


    def _get(self, id):
        if self.CONEXAO_BANCO.isConnOpen is False:
            self.CONEXAO_BANCO.abrirConexao()
        
        results = self.CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE cache_file = ?", (id,))

        self.CONEXAO_BANCO.salvarAlteracoes()
        self.CONEXAO_BANCO.fecharConexao()
        return results


    #Versão desenvolvida por causa do _get_fun_name, que diferente do _get, recebe o nome da função ao invés do id, serve para a v0.2.5.x e a v0.2.6.x, que tem o nome da função
    def _get_fun_name(self, fun_name):
        if self.CONEXAO_BANCO.isConnOpen is False:
            self.CONEXAO_BANCO.abrirConexao()

        results = self.CONEXAO_BANCO.executarComandoSQLSelect("SELECT cache_file FROM CACHE WHERE fun_name = ?", (fun_name,))

        self.CONEXAO_BANCO.salvarAlteracoes()
        self.CONEXAO_BANCO.fecharConexao()
        return results


    def _remove(self, id):
        if self.CONEXAO_BANCO.isConnOpen is False:
            self.CONEXAO_BANCO.abrirConexao()

        self.CONEXAO_BANCO.executarComandoSQLSemRetorno("DELETE FROM CACHE WHERE cache_file = ?;", (id,))

        self.CONEXAO_BANCO.salvarAlteracoes()
        self.CONEXAO_BANCO.fecharConexao()


    def _get_id(self, fun_args, fun_source):
        if self.g_argsp_hash[0] == 'md5':
            return hashlib.md5((str(fun_args) + fun_source).encode('utf')).hexdigest()
        elif self.g_argsp_hash[0] == 'murmur':
            return hex(mmh3.hash128((str(fun_args) + fun_source).encode('utf')))[2:]
        elif self.g_argsp_hash[0] == 'xxhash':
            return xxhash.xxh128_hexdigest((str(fun_args) + fun_source).encode('utf'))

    @staticmethod
    def _get_file_name(id):
        return "{0}.{1}".format(id, "ipcache")


    def _autofix(self, id):
        debug("starting autofix")
        debug("removing {0} from database".format(id))
        self._remove(self._get_file_name(id))
        debug("environment fixed")


    def _deserialize(self, id):
        try:
            with open(".intpy/cache/{0}".format(self._get_file_name(id)), 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError as e:
            warn("corrupt environment. Cache reference exists for a function in database but there is no file for it in cache folder.\
                Have you deleted cache folder?")
            self._autofix(id)
            return None


    def _serialize(return_value, file_name):
        with open(".intpy/cache/{0}".format(self._get_file_name(file_name)), 'wb') as file:
            return pickle.dump(return_value, file, protocol=pickle.HIGHEST_PROTOCOL)


    def _get_cache_data_v01x(self, id):
        list_file_name = self._get(self._get_file_name(id))
        return self._deserialize(id) if len(list_file_name) == 1 else None


    def _get_cache_data_v021x(self, id):
        #Nesta versão, DATA_DICTIONARY armazena os dados novos ainda não
        #persistidos no banco de dados

        if(id in self.DATA_DICTIONARY):
            return self.DATA_DICTIONARY[id]
        list_file_name = self._get(self._get_file_name(id))
        return self._deserialize(id) if len(list_file_name) == 1 else None


    def _get_cache_data_v022x(self, id):
        #Nesta versão, DATA_DICTIONARY armazena os dados novos ainda não
        #persistidos no banco de dados e os dados já persitidos no banco de dados

        if(id in self.DATA_DICTIONARY):
            return self.DATA_DICTIONARY[id]
        return None


    def _get_cache_data_v023x(self, id):
        if(id in self.DATA_DICTIONARY):
            return self.DATA_DICTIONARY[id]    
        if(id in self.NEW_DATA_DICTIONARY):
            return self.NEW_DATA_DICTIONARY[id]
        return None


    def _get_cache_data_v024x(self, id):
        with self.CACHED_DATA_DICTIONARY_SEMAPHORE:
            if(id in self.DATA_DICTIONARY):
                return self.DATA_DICTIONARY[id]
        if(id in self.NEW_DATA_DICTIONARY):
            return self.NEW_DATA_DICTIONARY[id]
        return None


    def _get_cache_data_v025x(self, id, fun_name):
        if(fun_name in self.FUNCTIONS_ALREADY_SELECTED_FROM_DB):
            if(id in self.DATA_DICTIONARY):
                return self.DATA_DICTIONARY[id]
            if(id in self.NEW_DATA_DICTIONARY):
                #Nesta versão, os valores de NEW_DATA_DICTIONARY são a tupla
                #(retorno_da_funcao, nome_da_funcao)
                return self.NEW_DATA_DICTIONARY[id][0]
        else:
            list_file_names = self._get_fun_name(fun_name)
            for file_name in list_file_names:
                file_name = file_name[0].replace(".ipcache", "")
                
                result = self._deserialize(file_name)
                if(result is None):
                    continue
                else:
                    self.DATA_DICTIONARY[file_name] = result

            self.FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(fun_name)
            if(id in self.DATA_DICTIONARY):
                return self.DATA_DICTIONARY[id]
        return None


    def _get_cache_data_v026x(self, id, fun_name):
        if(fun_name in self.FUNCTIONS_ALREADY_SELECTED_FROM_DB):
            with self.CACHED_DATA_DICTIONARY_SEMAPHORE:
                if(id in self.DATA_DICTIONARY):
                    return self.DATA_DICTIONARY[id]
            if(id in self.NEW_DATA_DICTIONARY):
                #Nesta versão, os valores de NEW_DATA_DICTIONARY são a tupla
                #(retorno_da_funcao, nome_da_funcao)
                return self.NEW_DATA_DICTIONARY[id][0]
        else:
            self.FUNCTIONS_ALREADY_SELECTED_FROM_DB.append(fun_name)        
            id_file_name = self._get_file_name(id)
            list_file_names = self._get_fun_name(fun_name)
            for file_name in list_file_names:
                if(file_name[0] == id_file_name):
                    thread = threading.Thread(target=self.add_new_data_to_CACHED_DATA_DICTIONARY, args=(list_file_names,))
                    thread.start()

                    file_name = file_name[0].replace(".ipcache", "")
                    return self._deserialize(file_name)
            
            thread = threading.Thread(target=self.add_new_data_to_CACHED_DATA_DICTIONARY, args=(list_file_names,))
            thread.start()
        return None


    #Comparável à versão v021x, mas com 2 dicionários
    def _get_cache_data_v027x(self, id):
        if(id in self.DATA_DICTIONARY):
            return self.DATA_DICTIONARY[id]
        if(id in self.NEW_DATA_DICTIONARY):
            return self.NEW_DATA_DICTIONARY[id]
        
        list_file_name = self._get(self._get_file_name(id))
        result = self._deserialize(id) if len(list_file_name) == 1 else None
        if(result is not None):
            self.DATA_DICTIONARY[id] = result
        return result



    def _get_cache_data_v2dmp(self, id):
        if (id in self.DATA_DICTIONARY):
            return self.DATA_DICTIONARY[id]
        
        list_file_name = self._get(self._get_file_name(id))
        result = self._deserialize(id) if len(list_file_name) == 1 else None
        if(result is not None):
            self.DATA_DICTIONARY[id] = result
            self.NEW_DATA_DICTIONARY[id] = result
        return result


    # Aqui misturam as versões v0.2.1.x a v0.2.7.x e v01x
    def get_cache_data(self, fun_name, fun_args, fun_source, argsp_v):
        id = self._get_id(fun_args, fun_source)

        if(argsp_v == ['v01x']):
            ret_get_cache_data_v01x = self._get_cache_data_v01x(id)
            return ret_get_cache_data_v01x
        elif(argsp_v == ['1d-ow'] or argsp_v == ['v021x']):
            ret_get_cache_data_v021x = self._get_cache_data_v021x(id)
            return ret_get_cache_data_v021x
        elif(argsp_v == ['1d-ad'] or argsp_v == ['v022x']):
            ret_get_cache_data_v022x = self._get_cache_data_v022x(id)
            return ret_get_cache_data_v022x
        elif(argsp_v == ['2d-ad'] or argsp_v == ['v023x']):
            ret_get_cache_data_v023x = self._get_cache_data_v023x(id)
            return ret_get_cache_data_v023x
        elif(argsp_v == ['2d-ad-t'] or argsp_v == ['v024x']):
            ret_get_cache_data_v024x = self._get_cache_data_v024x(id)
            return ret_get_cache_data_v024x
        elif(argsp_v == ['2d-ad-f'] or argsp_v == ['v025x']):
            ret_get_cache_data_v025x = self._get_cache_data_v025x(id, fun_name)
            return ret_get_cache_data_v025x
        elif(argsp_v == ['2d-ad-ft'] or argsp_v == ['v026x']):
            ret_get_cache_data_v026x = self._get_cache_data_v026x(id, fun_name)
            return ret_get_cache_data_v026x
        elif(argsp_v == ['2d-lz'] or argsp_v == ['v027x']):
            ret_get_cache_data_v027x = self._get_cache_data_v027x(id)
            return ret_get_cache_data_v027x
        elif(argsp_v == ['2d-mp']):
            return self._get_cache_data_v2dmp(id)



    def add_new_data_to_CACHED_DATA_DICTIONARY(self, list_file_names):
        for file_name in list_file_names:
            file_name = file_name[0].replace(".ipcache", "")
            
            result = self._deserialize(file_name)
            if(result is None):
                continue
            else:
                with self.CACHED_DATA_DICTIONARY_SEMAPHORE:
                    self.DATA_DICTIONARY[file_name] = result


    # Aqui misturam as versões v0.2.1.x a v0.2.7.x e v01x
    def create_entry(self, fun_name, fun_args, fun_return, fun_source, argsp_v):
        id = self._get_id(fun_args, fun_source)
        if argsp_v == ['v01x']:
            debug("serializing return value from {0}".format(id))
            self._serialize(fun_return, id)
            debug("inserting reference in database")
            self._save(self._get_file_name(id))

        elif(argsp_v == ['1d-ow'] or argsp_v == ['v021x'] or
            argsp_v == ['1d-ad'] or argsp_v == ['v022x']):
            self.DATA_DICTIONARY[id] = fun_return
        elif(argsp_v == ['2d-ad'] or argsp_v == ['v023x'] or 
            argsp_v == ['2d-ad-t'] or argsp_v == ['v024x'] or
            argsp_v == ['2d-lz'] or argsp_v == ['v027x']):
            self.NEW_DATA_DICTIONARY[id] = fun_return
        elif(argsp_v == ['2d-ad-f'] or argsp_v == ['v025x'] or
            argsp_v == ['2d-ad-ft'] or argsp_v == ['v026x']):
            self.NEW_DATA_DICTIONARY[id] = (fun_return, fun_name)


    # Aqui misturam as versões v0.2.1.x a v0.2.7.x
    def salvarNovosDadosBanco(self, argsp_v):
        if(argsp_v == ['1d-ow'] or argsp_v == ['v021x'] or
            argsp_v == ['1d-ad'] or argsp_v == ['v022x']):
            for id in self.DATA_DICTIONARY:
                debug("serializing return value from {0}".format(id))
                self._serialize(self.DATA_DICTIONARY[id], id)
                debug("inserting reference in database")
                self._save(self._get_file_name(id))
        
        elif(argsp_v == ['2d-ad'] or argsp_v == ['v023x'] or
            argsp_v == ['2d-ad-t'] or argsp_v == ['v024x'] or
            argsp_v == ['2d-lz'] or argsp_v == ['v027x']):
            for id in self.NEW_DATA_DICTIONARY:
                debug("serializing return value from {0}".format(id))
                self._serialize(self.NEW_DATA_DICTIONARY[id], id)
                debug("inserting reference in database")
                self._save(self._get_file_name(id))
        
        elif(argsp_v == ['2d-ad-f'] or argsp_v == ['v025x'] or
            argsp_v == ['2d-ad-ft'] or argsp_v == ['v026x']):
            for id in self.NEW_DATA_DICTIONARY:
                debug("serializing return value from {0}".format(id))
                self._serialize(self.NEW_DATA_DICTIONARY[id][0], id)
                debug("inserting reference in database")
                self._save_fun_name(self._get_file_name(id), self.NEW_DATA_DICTIONARY[id][1])



