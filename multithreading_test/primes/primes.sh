#!/bin/bash

n=1000000
num_threads=4
num_procs=4

# importante: ao rodar o shell script desta forma (rodando os 3 arquivos em cada iteração do loop)
# os resultados são inconsistentes os resultados das primeiras iterações parecem demorar mais (?)
# preferir executar um arquivo por loop

for i in {1..5}; do
    python multithreading_test\\primes\\primes.py ${n}
    C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python313\\python3.13t multithreading_test\\primes\\primes_multithreaded.py ${n} ${num_threads}
    python multithreading_test\\primes\\primes_multiprocessing.py ${n} ${num_procs}
done


