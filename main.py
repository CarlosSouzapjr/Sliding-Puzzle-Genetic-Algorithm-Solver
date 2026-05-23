from game_logic import GameLogic
from genetic_algorithm import GeneticAlgorithm
import copy

# Define o tamanho do puzzle (ex: 3x3)
tamanho_puzzle = 5

# Cria e embaralha o jogo original
jogo = GameLogic(tamanho_puzzle)
print("Tabuleiro Original (Resolvido):")
print(jogo.board)

jogo.randomize(moves=50) # Embaralha o tabuleiro com 50 movimentos aleatórios
print("\nTabuleiro Embaralhado (Problema Inicial):")
print(jogo.board)
print("-" * 30)

jogo = copy.deepcopy(jogo)

# Hiperparâmetros do Algoritmo Genético
tamanho_populacao = 100
tamanho_cromossomo = 100   # Número máximo de movimentos permitidos na solução (Tem que ser maior que o número de mover do randomizer para garantir que exista uma solução possível)
taxa_mutacao = 0.05       # 5% de chance de mutação por gene
max_geracoes = 100

ag = GeneticAlgorithm(
    population_size=tamanho_populacao,
    chromosome_length=tamanho_cromossomo,
    mutation_rate=taxa_mutacao,
    generations=max_geracoes,
    problem=jogo
)

# Roda o AG para encontrar a melhor solução
melhor_solucao = ag.run()

if melhor_solucao is not None:
    melhor_solucao = [str(move) for move in melhor_solucao] # convertendo np.str para string legível

print(f"\nMelhor sequência de movimentos encontrada ({len(melhor_solucao)} movimentos):")
print(melhor_solucao)

if melhor_solucao is None:
    print("\nO algoritmo não encontrou uma solução com esses parâmetros.")
else:
    # Jogar os movimentos encontrados para verificar o resultado
    jogo.play_moves(melhor_solucao)
    print("\nTabuleiro após aplicar os movimentos:\n")
    print(jogo.board)
    print("Resolvido:", jogo.is_solved())
