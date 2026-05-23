from game_logic import GameLogic
from genetic_algorithm import GeneticAlgorithm
import copy
# Define o tamanho do puzzle (ex: 3x3)
tamanho_puzzle = 3

# Cria e embaralha o jogo original
jogo = GameLogic(tamanho_puzzle)
print("Tabuleiro Original (Resolvido):")
print(jogo.board)

# Embaralha com 20 movimentos aleatórios (para não ficar impossível nos testes iniciais)
jogo.randomize(moves=20)
print("\nTabuleiro Embaralhado (Problema Inicial):")
print(jogo.board)
print("-" * 30)

jogo = copy.deepcopy(jogo)

# Configura os hiperparâmetros do Algoritmo Genético
# DICA: Ajuste esses valores durante os testes
tamanho_populacao = 100
tamanho_cromossomo = 30   # Um pouco maior que o número de embaralhamentos
taxa_mutacao = 0.05       # 5% de chance de mutação por gene
max_geracoes = 200

# Instancia o AG
ag = GeneticAlgorithm(
    population_size=tamanho_populacao,
    chromosome_length=tamanho_cromossomo,
    mutation_rate=taxa_mutacao,
    generations=max_geracoes,
    problem=jogo
)

# Roda a evolução!
melhor_solucao = ag.run()

print("\nMelhor sequência de movimentos encontrada:")
print(melhor_solucao)

if melhor_solucao is None:
    print("\nO algoritmo não encontrou uma solução com esses parâmetros.")
else:
    # Jogar os movimentos encontrados para verificar o resultado
    print("\nAplicando a melhor sequência de movimentos no tabuleiro embaralhado...")
    jogo.play_moves(melhor_solucao)
    print("Tabuleiro após aplicar os movimentos:")
    print(jogo.board)
    print("Resolvido:", jogo.is_solved())
