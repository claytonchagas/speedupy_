#import os
#from .banco import Banco
from intpy import _initialize_cache

graph = _initialize_cache()

#from .environment import init_env


#init_env()
#CONEXAO_BANCO = Banco(os.path.join(".intpy", "intpy.db"))

#This import is necessary because when it is executed, a select query to
#the database is started an all the data is brought and included in the
#DATA_DICTIONARY defined at that file
#from .data_access import *
