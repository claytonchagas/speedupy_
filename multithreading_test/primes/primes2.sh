#!/bin/bash

n=10000000
num_threads=4
num_procs=4

for i in {1..5}; do
    python multithreading_test\\primes\\primes.py ${n}
done

for i in {1..5}; do
    C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python313\\python3.13t multithreading_test\\primes\\primes_multithreaded.py ${n} ${num_threads}
done

for i in {1..5}; do
    python multithreading_test\\primes\\primes_multiprocessing.py ${n} ${num_procs}
done