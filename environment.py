import os
#import ctypes
from banco import Banco

from logger.log import debug

FOLDER_NAME = ".intpy"
CACHE_FOLDER_NAME = FOLDER_NAME + "/cache"
HIDDEN = 0x02
inter_cache = False


def _create_cache_folder():
    if _cache_folder_exists():
        debug("cache folder already exists")
        return

    debug("creating cache folder")
    os.makedirs(CACHE_FOLDER_NAME)


def _create_folder():
    debug("creating .intpy folder")
    if _folder_exists():
        debug(".intpy folder already exists")
        return

    os.makedirs(FOLDER_NAME)
    #ctypes.windll.kernel32.SetFileAttributesW(FOLDER_NAME, HIDDEN)


def init_env():
    global inter_cache
    if _folder_exists() is True:
        inter_cache = True
    
    debug("cheking if intpy environment exists")
    if _env_exists():
        debug("environment already exists")
        return
    

    debug("creating intpy environment")
    _create_folder()
    _create_cache_folder()
    _create_database()


def get_inter_cache_value():
    return inter_cache


def _create_database():
    debug("creating database")
    if _db_exists():
        debug("database already exists")
        return

    _create_table()


def _create_table():
    debug("creating table")
    conexaoBanco = Banco('.intpy/intpy.db')

    stmt = "CREATE TABLE IF NOT EXISTS CACHE (\
    id INTEGER PRIMARY KEY AUTOINCREMENT,\
    cache_file TEXT UNIQUE,\
    fun_name TEXT\
    );"

    conexaoBanco.executarComandoSQLSemRetorno(stmt)

    conexaoBanco.fecharConexao()


def _db_exists():
    return os.path.isfile('.intpy/intpy.db')


def _folder_exists():
    return os.path.exists(FOLDER_NAME)


def _cache_folder_exists():
    return os.path.exists(CACHE_FOLDER_NAME)


def _env_exists():
    return _folder_exists() and _db_exists() and _cache_folder_exists()
