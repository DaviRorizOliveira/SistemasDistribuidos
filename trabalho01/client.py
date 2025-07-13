import xmlrpc.client
import time

# Função para exibir o tabuleiro no terminal
def exibir_tabuleiro(tabuleiro):
    print("\n  1 2 3 4 5")
    for i, linha in enumerate(tabuleiro, 1):
        print(f"{i} {' '.join(linha)}")
    print()

# Função principal do cliente
def iniciar_cliente():
    # Conecta ao servidor
    servidor = xmlrpc.client.ServerProxy("http://localhost:8000", allow_none = True)

    # Registra o jogador
    nome = input("Qual é o seu nome? ")
    sucesso, mensagem = servidor.registrar_jogador(nome)
    print(mensagem)
    if not sucesso:
        return

    # Loop principal do jogo
    while True:
        # Obtém o status do jogo
        status = servidor.obter_status_jogo(nome)
        print(status)

        # Exibe o tabuleiro
        tabuleiro = servidor.obter_tabuleiro()
        exibir_tabuleiro(tabuleiro)

        # Verifica se o jogo terminou
        if "O jogo terminou" in status:
            break

        # Se for a vez do jogador, realiza a jogada
        if f"{nome} (" in status:
            try:
                linha = int(input("Digite a linha (1-5): "))
                coluna = int(input("Digite a coluna (1-5): "))
                sucesso, mensagem = servidor.fazer_jogada(nome, linha, coluna)
                print(mensagem)
                if not sucesso:
                    continue
            except ValueError:
                print("Por favor, digite números válidos.")
                continue
        else:
            print("Aguardando outros jogadores...")
            time.sleep(2) # Evita chamadas excessivas ao servidor

if __name__ == "__main__":
    iniciar_cliente()