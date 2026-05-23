import numpy as np
import copy

class GeneticAlgorithm:
    def __init__(self, population_size, chromosome_length, mutation_rate, generations, problem):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.mutation_rate = mutation_rate
        self.generations = generations
        
        self.problem = problem
        self.directions = ['up', 'down', 'left', 'right']
        
        total_pieces = self.problem.size * self.problem.size
        self.target_state = np.arange(1, total_pieces + 1)

    def create_chromosome(self):
        return [np.random.choice(self.directions) for _ in range(self.chromosome_length)]

    def create_population(self):
        return [self.create_chromosome() for _ in range(self.population_size)]

    def calculate_fitness(self, chromosome):
        simulated_game = copy.deepcopy(self.problem)
        moves_used = 0
        
        for move in chromosome:
            simulated_game.move(move)
            moves_used += 1
            
            if simulated_game.is_solved():
                max_moves_allowed = len(chromosome)
                fitness = 10000 + (max_moves_allowed - moves_used)
                return fitness
            
        current_state = simulated_game.board.flatten()
        
        correct_pieces = np.sum(current_state == self.target_state)
        fitness = correct_pieces
            
        return fitness
    
    def crossover(self, parent1, parent2):
        """
        Realiza o cruzamento de ponto único entre dois pais para gerar dois filhos.
        """
        # Escolhe um ponto de corte aleatório (garantindo que não seja no início ou fim absoluto)
        crossover_point = np.random.randint(1, self.chromosome_length - 1)
        
        # Cria os filhos combinando as metades dos pais
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2

    def mutate(self, chromosome):
        """
        Aplica mutação gene a gene no cromossomo, baseando-se na mutation_rate.
        """
        mutated_chromosome = []
        
        for gene in chromosome:
            # np.random.rand() gera um float entre 0.0 e 1.0
            if np.random.rand() < self.mutation_rate:
                # Ocorre a mutação: escolhe uma direção aleatória nova
                mutated_chromosome.append(np.random.choice(self.directions))
            else:
                # Mantém o gene original
                mutated_chromosome.append(gene)
                
        return mutated_chromosome
    
    def tournament_selection(self, population, fitness_scores, tournament_size=3):
        """
        Realiza a seleção por torneio para escolher um pai.
        
        :param population: Lista de cromossomos (a população atual).
        :param fitness_scores: Lista com as notas de fitness correspondentes a cada cromossomo.
        :param tournament_size: Número de indivíduos que vão competir (k).
        :return: O cromossomo vencedor.
        """
        # Sorteia índices aleatórios da população sem repetição (replace=False)
        tournament_indices = np.random.choice(len(population), size=tournament_size, replace=False)
        
        # Pega as notas dos indivíduos sorteados
        tournament_fitnesses = [fitness_scores[i] for i in tournament_indices]
        
        # Encontra o índice do vencedor (aquele com a maior nota no torneio)
        # np.argmax retorna a posição do maior valor no array do torneio
        winner_local_index = np.argmax(tournament_fitnesses)
        
        # Mapeia de volta para o índice original na população e retorna o cromossomo
        winner_global_index = tournament_indices[winner_local_index]
        
        return population[winner_global_index]
    
    def run(self):
        """
        Executa o loop do Algoritmo Genético por todas as gerações,
        buscando otimizar o tamanho da solução.
        """
        print("Iniciando o Algoritmo Genético...")
        
        # Inicializa a primeira população aleatória
        population = self.create_population()
        
        best_overall_chromosome = None
        best_overall_fitness = -1

        for generation in range(self.generations):
            # Avalia o fitness de todos os indivíduos da população
            fitness_scores = [self.calculate_fitness(chrom) for chrom in population]
            
            # Encontra o melhor indivíduo da geração atual
            current_best_idx = np.argmax(fitness_scores)
            current_best_chromosome = population[current_best_idx]
            current_best_fitness = fitness_scores[current_best_idx]

            # ATUALIZA O RECORDE GLOBAL:
            # Como menor número de passos = maior fitness, isso garante 
            # que guardaremos sempre a solução MAIS CURTA encontrada até aqui.
            if current_best_fitness > best_overall_fitness:
                best_overall_fitness = current_best_fitness
                best_overall_chromosome = current_best_chromosome

            # Mostramos o melhor da geração e o melhor absoluto para acompanhar a evolução
            print(f"Geração {generation:04d} | Melhor da Gen: {current_best_fitness} | Melhor Global: {best_overall_fitness}")

            # Criação da Próxima Geração
            new_population = []

            # ELITISMO: Mantém o melhor da geração atual para a próxima
            new_population.append(current_best_chromosome)

            # Preenche o resto da população
            while len(new_population) < self.population_size:
                parent1 = self.tournament_selection(population, fitness_scores)
                parent2 = self.tournament_selection(population, fitness_scores)
                child1, child2 = self.crossover(parent1, parent2)
                
                new_population.append(self.mutate(child1))
                if len(new_population) < self.population_size:
                    new_population.append(self.mutate(child2))

            population = new_population

        # Verificar se a melhor solução global encontrada resolve o puzzle
        if best_overall_fitness >= 10000:
            # Matemática reversa para descobrir quantos movimentos foram úteis
            moves_used = int(self.chromosome_length - (best_overall_fitness - 10000))
            
            # Corta o cromossomo mantendo apenas os passos estritamente necessários
            trimmed_chromosome = best_overall_chromosome[:moves_used]
            
            final_chromosome = trimmed_chromosome
        else:
            final_chromosome = best_overall_chromosome
        
        print(f"\n>>> FIM DAS GERAÇÕES! Melhor solução encontrada com fitness: {best_overall_fitness} <<<")
        
        return final_chromosome