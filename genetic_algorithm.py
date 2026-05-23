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
        Executa o loop principal do Algoritmo Genético.
        """
        print("Iniciando o Algoritmo Genético...")
        
        # 1. Inicializa a primeira população aleatória
        population = self.create_population()
        
        best_overall_chromosome = None
        best_overall_fitness = -1

        for generation in range(self.generations):
            # 2. Avalia o fitness de todos os indivíduos da população
            fitness_scores = [self.calculate_fitness(chrom) for chrom in population]
            
            # 3. Encontra o melhor indivíduo da geração atual
            current_best_idx = np.argmax(fitness_scores)
            current_best_chromosome = population[current_best_idx]
            current_best_fitness = fitness_scores[current_best_idx]

            # Atualiza o recorde global
            if current_best_fitness > best_overall_fitness:
                best_overall_fitness = current_best_fitness
                best_overall_chromosome = current_best_chromosome

            # Imprime o progresso (a cada 10 gerações para não floodar o terminal)
            if generation % 10 == 0 or generation == self.generations - 1:
                print(f"Geração {generation:04d} | Melhor Fitness: {current_best_fitness}")


            # 5. Criação da Próxima Geração
            new_population = []

            # ELITISMO: Salva o melhor indivíduo intacto (sem mutação/cruzamento)
            # Isso garante que a nossa melhor solução nunca seja perdida por azar
            new_population.append(current_best_chromosome)

            # Preenche o resto da população
            while len(new_population) < self.population_size:
                # Seleciona dois pais via Torneio
                parent1 = self.tournament_selection(population, fitness_scores)
                parent2 = self.tournament_selection(population, fitness_scores)

                # Cruza os pais para gerar dois filhos
                child1, child2 = self.crossover(parent1, parent2)

                # Aplica a mutação no primeiro filho e o adiciona à população
                new_population.append(self.mutate(child1))
                
                # Checa o limite para não exceder o tamanho da população (caso seja ímpar)
                if len(new_population) < self.population_size:
                    # Aplica a mutação no segundo filho e o adiciona
                    new_population.append(self.mutate(child2))

            # A nova geração substitui a antiga
            population = new_population

        # Se o loop terminar sem encontrar a solução perfeita
        print(f"Melhor fitness alcançado: {best_overall_fitness}")
        return best_overall_chromosome