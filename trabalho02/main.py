import numpy as np
import os
import time
from multiprocessing import Pool, Queue, Process

'''
Biblioteca 'numpy' para manipulação de matrizes

Biblioteca 'os' para manipulação de arquivos

Biblioteca 'time' para medição de tempo

Biblioteca 'multiprocessing' utilizada para realizar os cálculos em paralelo

Pool: Gerencia processos
Queue: Comunicação entre processos
Process: Cria processos individuais
'''

# Calcula o determinante da matriz
def determinante(matrix):
    return np.linalg.det(matrix)

# Calcula a inversa de uma matriz usando cofatores
def matriz_inversa(matrix):
    det = np.linalg.det(matrix)
    if abs(det) < 1e-10: # Tolerância para zero
        raise ValueError("Matriz nao inversivel")
    return np.linalg.inv(matrix)

# Calcula um bloco de linhas da multiplicação de matrizes A x B
def multiplicacao_por_bloco(args):
    bloco_A, B, offset, linhas = args
    result = np.zeros((linhas, B.shape[1]))
    for i in range(linhas):
        for k in range(B.shape[1]):
            for j in range(bloco_A.shape[1]):
                result[i][k] += bloco_A[i][j] * B[j][k]
    return offset, result

# Realiza multiplicação de matrizes A x B de forma paralela usando multiprocessing
def multiplicacao_paralela(A, B, num_processos):
    n = A.shape[0]
    linhas_por_processo = n // num_processos if num_processos > 1 else n
    result = np.zeros((n, n))

    # Divide a matriz A em blocos
    tasks = [] # Lista de tarefas
    offset = 0
    for i in range(num_processos):
        rows = linhas_por_processo if i < num_processos - 1 else n - offset
        if rows > 0:
            tasks.append((A[offset : offset + rows], B, offset, rows))
            offset += rows

    # Executa multiplicações em paralelo
    with Pool(processes = num_processos) as pool:
        results = pool.map(multiplicacao_por_bloco, tasks)

    # Combina os resultados
    for offset, partial_result in results:
        result[offset : offset + partial_result.shape[0]] = partial_result

    return result

# Realiza multiplicação de matrizes A x B de forma sequencial
def multiplicacao_sequencial(A, B):
    n = A.shape[0]
    m = B.shape[1]
    p = A.shape[1]
    result = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            for k in range(p):
                result[i][j] += A[i][k] * B[k][j]
    return result

# Calcula o determinante e coloca o resultado na fila
def calc_det(matrix, queue):
    queue.put(determinante(matrix))

# Calcula o determinante de M usando a fórmula de Schur com multiprocessing
def schur_paralelo(A, B, C, D, num_processos):
    # Verifica se A é inversível
    det_a = determinante(A)
    if abs(det_a) < 1e-10: # Tolerância para zero
        raise ValueError("A nao eh inversivel")

    # Calcula A^{-1}
    A_inv = matriz_inversa(A)

    # Calcula CA^{-1}B em paralelo
    C_A_inv = multiplicacao_paralela(C, A_inv, num_processos)
    CA_inv_B = multiplicacao_paralela(C_A_inv, B, num_processos)

    # Calcula D - CA^{-1}B
    D_minus = D - CA_inv_B

    # Calcula determinantes em paralelo
    queue = Queue()
    p1 = Process(target = calc_det, args = (A, queue))
    p2 = Process(target = calc_det, args = (D_minus, queue))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()

    det_a = queue.get()
    det_d_minus = queue.get()

    return det_a * det_d_minus

# Calcula o determinante de M usando a fórmula de Schur de forma sequencial
def schur_sequencial(A, B, C, D):
    # Verifica se A é inversível
    det_a = determinante(A)
    if abs(det_a) < 1e-10: # Tolerância para zero
        raise ValueError("A nao eh inversivel")

    # Calcula A^{-1}
    A_inv = matriz_inversa(A)

    # Calcula CA^{-1}B de forma sequencial
    C_A_inv = multiplicacao_sequencial(C, A_inv)
    CA_inv_B = multiplicacao_sequencial(C_A_inv, B)

    # Calcula D - CA^{-1}B
    D_minus = D - CA_inv_B

    # Calcula determinantes
    det_d_minus = determinante(D_minus)

    return det_a * det_d_minus

# Monta a matriz com base nos dados do arquivo de entrada
def monta_matriz(lines, start_id, n):
    matriz = np.zeros((n, n))
    for i in range(n):
        valor = [float(x) for x in lines[start_id + i].split()]
        matriz[i] = valor
    return matriz, start_id + n

def main():
    # Obtém o diretório atual do arquivo e cria os caminhos para os arquivos de entrada e saída
    diretorio = os.path.dirname(os.path.realpath(__file__))
    inputs = os.path.join(diretorio, "in.txt")
    outputs = os.path.join(diretorio, "out.txt")

    # Lê as entradas do arquivo de entrada
    try:
        with open(inputs, "r") as arq:
            lines = arq.readlines()
            i = 0
            entradas = []
            while i < len(lines):
                n = int(lines[i].strip())
                i += 1
                num_processos = int(lines[i].strip())
                i += 1
                A, idx = monta_matriz(lines, i, n)
                i = idx
                B, idx = monta_matriz(lines, i, n)
                i = idx
                C, idx = monta_matriz(lines, i, n)
                i = idx
                D, idx = monta_matriz(lines, i, n)
                i = idx
                entradas.append((A, B, C, D, num_processos))
    except FileNotFoundError:
        print("Erro: Arquivo in.txt nao encontrado.")
        return
    except Exception as e:
        print(f"Erro ao ler o arquivo: {str(e)}")
        return

    # Calcula o determinante para cada entrada e escreve no arquivo de saída
    with open(outputs, "w") as arq:
        for A, B, C, D, num_processos in entradas:
            try:
                # Calcula e mede o tempo do método paralelo
                start_time = time.time()
                result_paralelo = schur_paralelo(A, B, C, D, num_processos)
                tempo_paralelo = time.time() - start_time

                # Calcula e mede o tempo do método sequencial
                start_time = time.time()
                result_sequencial = schur_sequencial(A, B, C, D)
                tempo_sequencial = time.time() - start_time

                # Escreve resultados
                arq.write(f'Resultado para as matrizes fornecidas (usando {num_processos} processos):\n')
                arq.write(f'Metodo Paralelo:\n')
                arq.write(f'\tDeterminante de M: {result_paralelo}\n')
                arq.write(f'\tTempo de execucao: {tempo_paralelo:.6f} segundos\n')
                arq.write(f'Metodo Sequencial:\n')
                arq.write(f'\tDeterminante de M: {result_sequencial}\n')
                arq.write(f'\tTempo de execucao: {tempo_sequencial:.6f} segundos\n\n')
            except Exception as e:
                arq.write(f'Erro no calculo: {str(e)}\n\n')

if __name__ == "__main__":
    main()