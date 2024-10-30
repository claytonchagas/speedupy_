import argparse
import sys


def usage_msg():
    return "\nIntPy's Python command line arguments help:\n\n\
To run your experiment with IntPy use:\n\
$ python "+str(sys.argv[0])+" program_arguments [-h, --help] [-g, --glossary] [-m memory|help, --memory memory|help] [-0, --no-cache] [-H type|help, --hash type|help] [-M method|help, --marshalling method|help] [-s form|help, --storage form|help]\n\n\
To run in the IntPy DEBUG mode use:\n\
$ DEBUG=True python "+str(sys.argv[0])+" program_arguments [-h, --help] [-g, --glossary] [-m memory|help, --memory memory|help] [-0, --no-cache] [-H type|help, --hash type|help] [-M method|help, --marshalling method|help] [-s form|help, --storage form|help]\n\n\
"
def glossary_msg():
    return hashes_msg() + marshalling_msg() + storage_msg() + memory_msg()

def hashes_msg():
    return "\nHashes: \n\
    =>md5   : is a cryptographic hash fuction with a better collision resistence and lower performance compared to the others.\n\
    =>murmur: is a modern non-cryptographic hash function with a low collision rate and high performance.\n\
    =>xxhash: is a modern non-cryptographic hash function with a lower collision resistence and better performance compered to murmur.\n\
    usage: $ python "+str(sys.argv[0])+" program_arguments -H|--hash options\
    \n"
def marshalling_msg():
    return "Marshalling:\n\
    =>Pickle:\n\
    usage: $ python "+str(sys.argv[0])+" program_arguments -M|--marshalling options\n\
    \n"

def storage_msg():
    return "Storage:\n\
    =>db-file: use database and file to store data.\n\
    =>db     : use database to store data\n\
    =>file   : use file to store data.\n\
    usage: $ python "+str(sys.argv[0])+" program_arguments -s|--storage options\
    \n"

def memory_msg():
    return "Memory forms:\n\
    =>ad      : original version with some bug fixes and instrumentation, all data are stored directly in the database.\n\
    =>1d-ow   : one dicionary (1d), only write (ow), 1st implementation of dictionary: new data is added to the dictionary only when cache miss occur and the function decorated with @deterministic is executed.\n\
    =>1d-ad   : one dicionary (1d), all data loaded at the begining (ad), 2nd implementation of dictionary (uses 1 dictionary): at the begining of the execution all the data cached is loaded to the dictonary before the user script starts to run.\n\
    =>2d-ad   : two dicionaries (2d), all data loaded at the begining (ad), 3rd implementation of dictionary (uses 2 dictionaries): at the begining of the execution all the data cached is loaded to the dictionary DATA_DICTIONARY before the user script starts to run. When cache miss occurs and a function decorated with @deterministic is processed, its result is stored in NEW_DATA_DICTIONARY. This way, only the elements of NEW_DATA_DICTIONARY are added to the database at the end of the execution.\n\
    =>2d-ad-t : two dicionaries (2d), all data loaded at the begining with a thread (ad-t), 4th implementation of dictionary (uses 2 dictionaries): at the begining of the execution a thread is started to load all the data cached in the database to the dictionary DATA_DICTIONARY. When cache miss occurs and a function decorated with @deterministic is processed, its result is stored in NEW_DATA_DICTIONARY. Only the elements of NEW_DATA_DICTIONARY are added to the database at the end of the execution but it is possible that some elements in NEW_DATA_DICTIONARY are already in the database due to the concurrent execution of the experiment and the thread that populates DATA_DICTIONARY.\n\
    =>2d-ad-f : two dicionaries (2d), all data loaded at the begining of a function(ad-f), 5th implementation of dictionary (uses 2 dictionaries): when @deterministic is executed a select query is created to the database to bring all results of the function decorated with @deterministic stored in the cache. A list of functions already inserted to the dictionary is maintained to avoid unecessary querys to the database. The results are then stored in the dictionary DATA_DICTIONARY. When cache miss occurs and a function decorated with @deterministic is processed, its result is stored in NEW_DATA_DICTIONARY. This way, only the elements of NEW_DATA_DICTIONARY are added to the database at the end of the execution.\n\
    =>2d-ad-ft: two dicionaries (2d), all data loaded at the begining of a function with a thread (ad-ft), 6th implementation of dictionary (uses 2 dictionaries): when @deterministic is executed a select query is created to the database to bring all results of the function decorated with @deterministic stored in the cache. A list of functions already inserted to the dictionary is maintained to avoid unecessary querys to the database. The results of the query are stored in the dictionary DATA_DICTIONARY by a thread. When cache miss occurs and a function decorated with @deterministic is processed, its result is stored in NEW_DATA_DICTIONARY. This way, only the elements of NEW_DATA_DICTIONARY are added to the database at the end of the execution.\n\
    =>2d-lz   : two dicionaries (2d), lazy mode (lz), 7th implementation of dictionary (uses 2 dictionaries): new data is added to DATA_DICTIONARY when cache hit occurs (LAZY approach) and new data is added to NEW_DATA_DICTIONARY when cache miss occur and the function decorated with @deterministic is executed.\n\
    =>2d-mp   : two dictonaries (2d), with multiprocessing, two processes are started, the result comes from the process that finishes first and kills the other. The first process executes the function normaly. The second process tries to find the cached data on DATA_DICTIONARY. If a cache hit occurs, returns the cached data. Otherwise, in a cache miss, queries for the cached data on the DB. If a query result is present, writes the data to DATA_DICTIONARY and returns the cached result, otherwise, returns None \n\
    usage: $ python "+str(sys.argv[0])+" program_arguments -m|--memory options\n\
    \n"
    

def get_params():
    memories = ['help','ad', '1d-ow', '1d-ad', '2d-ad', '2d-ad-t', '2d-ad-f', '2d-ad-ft', '2d-lz', '2d-mp']

    hashes = ['help','md5', 'murmur', 'xxhash']

    marshals = ['help','pickle']

    storageOptions = ['help','db-file','db','file']

    intpy_arg_parser = argparse.ArgumentParser(usage=usage_msg())

    
    intpy_arg_parser.add_argument('args',
                                   metavar='program arguments',
                                   nargs='*',
                                   type=str, 
                                   help='program arguments')
    
    intpy_arg_parser.add_argument('-m',
                                  '--memory',
                                   choices=memories,
                                   metavar='',
                                   nargs=1,
                                   type=str,
                                   default=['2d-ad'],
                                   help='IntPy\'s mechanism of persistence: choose one of the following options: '+', '.join(memories))
    
    intpy_arg_parser.add_argument('-H',
                                  '--hash',
                                   choices=hashes,
                                   metavar='',
                                   nargs=1,
                                   default=['md5'],
                                   help='SpeedUpy\'s mechanism of hashes: choose one of the following options: '+', '.join(hashes))
    
    intpy_arg_parser.add_argument('-g',
                                  '--glossary',
                                  default=False,
                                  action='store_true',
                                  help='show details of SpeedUpy versions')
   
    intpy_arg_parser.add_argument('-0',
                                  '--no-cache',
                                  default=False,
                                  action="store_true",
                                  help='SpeedUpy\'s disable cache')

    intpy_arg_parser.add_argument('-M',
                                  '--marshalling',
                                   choices=marshals,
                                   metavar='',
                                   nargs=1,
                                   default=['pickle'],
                                   help='SpeedUpy\'s mechanism of marshalling: choose one of the following options: '+', '.join(marshals))
    
    intpy_arg_parser.add_argument('-s',
                                  '--storage',
                                   choices=storageOptions,
                                   metavar='',
                                   nargs=1,
                                   default=['db-file'],
                                   help='SpeedUpy\'s mechanism of storage: choose one of the following options: '+', '.join(storageOptions))

    
    args = intpy_arg_parser.parse_args()

    
    if args.glossary:
        print(glossary_msg())
        sys.exit()
    
    argsp_m = args.memory

    argsp_s = args.storage

    argsp_M = args.marshalling

    argsp_no_cache = args.no_cache

    argsp_hash = args.hash


    if str(argsp_m[0]) == 'help' or str(argsp_M[0]) == 'help' or str(argsp_hash[0]) == 'help' or str(argsp_s[0]) == 'help':
        if str(argsp_m[0]) == 'help':
            print(memory_msg())
            
        if str(argsp_M[0]) == 'help':
            print(marshalling_msg())

        if str(argsp_hash[0]) == 'help':
            print(hashes_msg())

        if str(argsp_s[0]) == 'help':
            print(storage_msg())
        sys.exit()

    return argsp_m, argsp_M, argsp_s, argsp_no_cache, argsp_hash


"""
if argsp.version == ['1d-ow'] or argsp.version == ['v021x']:
    v_data_access = ".data_access_v021x_1d-ow"
elif argsp.version == ['1d-ad'] or argsp.version == ['v022x']:
    v_data_access = ".data_access_v022x_1d-ad"
elif argsp.version == ['2d-ad'] or argsp.version == ['v023x']:
    v_data_access = ".data_access_v023x_2d-ad"
elif argsp.version == ['2d-ad-t'] or argsp.version == ['v024x']:
    v_data_access = ".data_access_v024x_2d-ad-t"
elif argsp.version == ['2d-ad-f'] or argsp.version == ['v025x']:
    v_data_access = ".data_access_v025x_2d-ad-f"
elif argsp.version == ['2d-ad-ft'] or argsp.version == ['v026x']:
    v_data_access = ".data_access_v026x_2d-ad-ft"
elif argsp.version == ['2d-lz'] or argsp.version == ['v027x']:
    v_data_access = ".data_access_v027x_2d-lz"
else:
    v_data_access = ".data_access_v021x_1d-ow"
"""