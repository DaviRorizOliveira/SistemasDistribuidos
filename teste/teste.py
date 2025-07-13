import numpy as np
import os

def generate_matrix_A(n):
    matrix = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = np.random.randint(1, 11)
            elif j > i:
                matrix[i][j] = np.random.randint(0, 11)
    return matrix

def generate_matrix(n):
    return np.random.randint(0, 101, size=(n, n))

def write_input_file(n, num_processos, filename="in.txt"):
    A = generate_matrix_A(n)
    B = generate_matrix(n)
    C = generate_matrix(n)
    D = generate_matrix(n)

    diretorio = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(diretorio, filename)

    try:
        with open(filepath, "w") as f:
            f.write(f"{n}\n")
            f.write(f"{num_processos}\n")
            for matrix, name in [(A, "A"), (B, "B"), (C, "C"), (D, "D")]:
                for i in range(n):
                    row = [int(matrix[i][j]) for j in range(n)]
                    f.write(" ".join(map(str, row)) + "\n")
        print(f"Arquivo {filename} gerado com sucesso no diretório {diretorio}.")
    except Exception as e:
        print(f"Erro ao gerar o arquivo {filename}: {str(e)}")

def main():
    try:
        n = int(input("Digite o tamanho da matriz (n): "))
        if n <= 0:
            raise ValueError("n deve ser um inteiro positivo.")
        
        num_processos = int(input("Digite o número de processos (num_processos): "))
        if num_processos <= 0:
            raise ValueError("num_processos deve ser um inteiro positivo.")
        
        write_input_file(n, num_processos)
    except ValueError as e:
        print(f"Erro: {str(e)}")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main()