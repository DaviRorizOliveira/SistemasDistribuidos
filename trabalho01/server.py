import xmlrpc.server
import threading

class JogoDaVelha:
    # Método que inicializa os atributos
    def __init__(self):
        self.tabuleiro = [[' ' for _ in range(5)] for _ in range(5)] # Tabuleiro 5x5
        self.jogadores = [] # Lista de nomes dos jogadores
        self.simbolos = ['X', 'O', 'Z'] # Símbolos dos jogadores
        self.jogador_atual = 0 # Índice do jogador atual
        self.inicio = False # Indica se o jogo começou
        self.block = threading.Lock() # Garante operações seguras entre threads
        self.vencedor = None # Vencedor do jogo

    # Método para registrar jogadores
    def registrar_jogador(self, nome):
        with self.block:
            # Impede a entrada de um "quarto jogador"
            if len(self.jogadores) >= 3:
                return False, "O jogo está cheio. Apenas três jogadores são permitidos."
            # Verifica se o nome já está em uso
            if nome in self.jogadores:
                return False, "O nome já está em uso. Por favor, escolha outro."
            # Registra o jogador
            self.jogadores.append(nome)
            # Inicia o jogo quando o terceiro jogador se registra
            if len(self.jogadores) == 3:
                self.inicio = True
            return True, f"Jogador {nome} registrado como {self.simbolos[len(self.jogadores) - 1]}."

    # Método que retorna o tabuleiro
    def obter_tabuleiro(self):
        return self.tabuleiro

    # Método para realizar jogadas
    def fazer_jogada(self, nome, linha, coluna):
        with self.block:
            if not self.inicio:
                return False, "O jogo ainda não começou. Aguardando todos os jogadores."
            # Verifica se o jogo terminou
            if self.vencedor or self.tabuleiro_cheio():
                return False, "O jogo terminou."
            if nome not in self.jogadores:
                return False, "Jogador desconhecido."
            if self.jogadores[self.jogador_atual] != nome:
                return False, "Não é sua vez. Espere mais um pouco."
            # Converte para o índice baseado em 0
            linha = linha - 1
            coluna = coluna - 1
            # Verifica se a posição é válida
            if not (0 <= linha < 5 and 0 <= coluna < 5):
                return False, "Posição inválida. Por favor, escolha outra posição."
            # Verifica se a posição já está ocupada
            if self.tabuleiro[linha][coluna] != ' ':
                return False, "Posição já ocupada. Por favor, escolha outra posição."

            # Realiza a jogada
            self.tabuleiro[linha][coluna] = self.simbolos[self.jogador_atual]
            # Verifica se houve vitória
            if self.verificar_vitoria(self.simbolos[self.jogador_atual]):
                self.vencedor = nome
                return True, f"Jogada aceita. {nome} venceu!"
            if self.tabuleiro_cheio():
                return True, "Jogada aceita. O jogo terminou em empate."

            # Atualiza o jogador que fará a próxima jogada
            self.jogador_atual = (self.jogador_atual + 1) % 3
            return True, "Jogada aceita."

    # Método para verificar vitória
    def verificar_vitoria(self, simbolo):
        # Verifica linhas
        for linha in self.tabuleiro:
            for i in range(3):
                if linha[i] == linha[i + 1] == linha[i + 2] == simbolo:
                    return True

        # Verifica colunas
        for col in range(5):
            for i in range(3):
                if (self.tabuleiro[i][col] == self.tabuleiro[i + 1][col] == self.tabuleiro[i + 2][col] == simbolo):
                    return True

        # Verifica diagonais principais
        for i in range(3):
            for j in range(3):
                if (self.tabuleiro[i][j] == self.tabuleiro[i + 1][j + 1] == self.tabuleiro[i + 2][j + 2] == simbolo):
                    return True

        # Verifica diagonais secundárias
        for i in range(3):
            for j in range(2, 5):
                if (self.tabuleiro[i][j] == self.tabuleiro[i + 1][j - 1] == self.tabuleiro[i + 2][j - 2] == simbolo):
                    return True

        return False

    # Método para verificar se o tabuleiro está cheio
    def tabuleiro_cheio(self):
        return all(celula != ' ' for linha in self.tabuleiro for celula in linha)

    # Método para obter o status do jogo
    def obter_status_jogo(self, nome_jogador):
        with self.block:
            if not self.inicio:
                return f"Aguardando {3 - len(self.jogadores)} jogador(es)."
            if self.vencedor:
                return f"O jogo terminou. {self.vencedor} venceu!"
            if self.tabuleiro_cheio():
                return "O jogo terminou. Empate."
            atual = self.jogadores[self.jogador_atual]
            return f"Jogador atual: {atual} ({self.simbolos[self.jogador_atual]})."

# Função para iniciar o servidor
def iniciar_servidor():
    # Cria o servidor na porta 8000 do localhost
    servidor = xmlrpc.server.SimpleXMLRPCServer(("localhost", 8000), allow_none = True)
    # Registra a instância da classe no servidor
    servidor.register_instance(JogoDaVelha())
    print("Servidor rodando em localhost:8000...")
    # Mantém o servidor ativo aguardando chamadas
    servidor.serve_forever()

if __name__ == "__main__":
    iniciar_servidor()