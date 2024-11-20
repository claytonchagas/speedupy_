#!/bin/bash

# teste do cenario 1 - com intra caching / sem inter caching
# teste do cenario 2 - com intra caching / com inter caching
# em cada iteração foi testado com os dois cenarios
n=100


for ((i = 1; i <= n; i++)); do
    rm -r .intpy
    python teste_multiprocessing.py $i -m 2d-mp -s db
    python teste_multiprocessing.py $i -m 2d-mp -s db
    echo 2d-mp / $i finalizado
done



for ((i = 1; i <= n; i++)); do
    rm -r .intpy
    python teste.py $i -m 2d-ad -s db
    python teste.py $i -m 2d-ad -s db
    echo 2d-mp / $i finalizado
done

