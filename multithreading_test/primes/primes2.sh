#!/bin/bash

# benchmarks do python 3.13

n=10000000
num_threads=4
num_procs=4

# 1) execução sequencial
for i in {1..5}; do
    python multithreading_test\\primes\\primes.py ${n}
done

# 2) execução com multithreading sem GIL 
# testes feitos com versão beta do 3.13
# (na versão beta) para desabilitar o GIL: é preciso utilizar o seguinte intrepretador - python3.13t
for i in {1..5}; do
    C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python313\\python3.13t multithreading_test\\primes\\primes_multithreaded.py ${n} ${num_threads}
done

# 3) execução com multiprocessamento
for i in {1..5}; do
    python multithreading_test\\primes\\primes_multiprocessing.py ${n} ${num_procs}
done