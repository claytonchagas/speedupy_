> **Repositório arquivado (novembro de 2026).** Esta é a primeira geração do SpeeduPy (2023), de arquivo único (`intpy.py`), mantida apenas como registro histórico. O desenvolvimento continua em **https://github.com/dew-uff/speedupy**, com arquitetura nova, testes e releases versionadas. As branches `lucas`, `multiprocessing` e `lanerson` guardam o trabalho de Lucas Martello Nogueira e Lanerson Farias (2024 e 2025) sobre execução com multiprocessamento e multithreading, feito sobre esta arquitetura e não portado.

# Speedupy
Essa ferramente foi desenvolvida como o objetivo de acelerar o tempo de execução de programas escritos em Python. 

## Como utilizar?

### Preparar diretórios

Vá até a pasta onde se encontre os programas que você deseja acelerar.
```bash
$ cd </caminho_pasta_programas> 

</caminho_pasta_programas>$ git clone https://github.com/claytonchagas/speedupy.git
```
No nosso caso, foi utilizada a pasta [speedupy_experiments-main](https://github.com/claytonchagas/speedupy_experiments), que pode ser obtida para teste da ferramenta clicando no link, depois disso basta descompacta-la.
```bash
$ cd Downloads/speedupy_experiments-main/01pilots/01pilots_exp01_fibonacci

~/Downloads/speedupy_experiments-main/01pilots/01pilots_exp01_fibonacci $ git clone https://github.com/claytonchagas/speedupy.git
```
### Preparar arquivos

Para que o framework consiga interpretar o código tempos que denotar ele com as seguintes decorators:
@deterministic - para cada função que vai ser acelerada
@initialize_intpy(\_\_file\_\_) - para a main()

Além disso é necessário que possuir a seguinte estrutura para chamar a função main:
if __name__ == "\_\_main\_\_":
    n = int(sys.argv[1])
    start = time.perf_counter()
    main(n)
    print(time.perf_counter()-start)

*passível de adaptação nos argumentos passados como parametros na main

Exemplo:

![image](https://github.com/claytonchagas/speedupy/assets/90840183/9dd0cab9-440f-496c-91a0-2d08e7dc0f66)

Figura 1: código adaptado do cálculo n-ésimo termo de fibonacci. 

![image](https://github.com/claytonchagas/speedupy/assets/90840183/d830f832-629b-4d10-bc19-acbf7cfcd4f8)

Figura 2: código adaptado do cálculo da potência, de um número n, a m. 

### Executar os programas
Uma vez que o programa já esteja adaptado, basta executá-lo.
```bash
$ python <nome_arquivo>.py program_params [-h, --help] [-g, --glossary] [-m memory|help, --memory memory|help] [-0, --no-cache] [-H type|help, --hash type|help] [-M method|help, --marshalling method|help] [-s form|help, --storage form|help]
```
para se ter uma ideia melhor, basta utilizar o argumento "-h" ou "--help", lá terá todos os argumentos válidos e suas entradas. 
```bash
python fibonacci.py -h
```

![image](https://github.com/claytonchagas/speedupy/assets/90840183/f865a7e1-cccc-48f0-b9c9-b77276352908)

Figura 3: utilização do -h

Uma vez descoberto os argumentos e seus respectivos parâmetros, podemos utiliza-los como pode ser explicitado na imagem abaixo:

![image](https://github.com/claytonchagas/speedupy/assets/90840183/dc537267-6b7b-45b7-9db0-3a13158024a1)

Figura 4: Exemplo da definição de alguns argumentos.

Por fim, caso se deseje saber mais sobre algum argumento específico, utilize o "help" após este argumento:

![image](https://github.com/claytonchagas/speedupy/assets/90840183/ffa4008d-61fb-418d-9e9e-2484e38e3702)


