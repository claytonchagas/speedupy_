import sys
import time
from intpy import deterministic, initialize_intpy


@deterministic
def fib(n):
    if n < 2:
        return n
    else:
        return fib(n-1) + fib(n-2)

@initialize_intpy(__file__)
def main(n):
    t0 = time.time()
    print(fib(n))
    print(time.time()-t0)
    

if __name__ =='__main__':      
    n = int(sys.argv[1])
    main(n)
