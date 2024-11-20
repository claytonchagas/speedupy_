#!/bin/bash

# teste do cenario 1 - com intra caching / sem inter caching
# neste cenário, todos os experimentos começam SEM o diretório .intpy, que tem os resultado do cache
n=10

rm -r .intpy


for ((i = 1; i <= n; i++)); do
    python teste_multiprocessing.py $i -m 2d-mp -s db
    rm -r .intpy
    echo 2d-mp / $i finalizado
done


for ((i = 1; i <= n; i++)); do
    python teste.py $i -m 2d-ad -s db
    rm -r .intpy
    echo 2d-ad / $i finalizado
done