import random
import copy
import math
from .__helpers import astar
from ..function.standard_layout_fitness import get_fitness

class Gasim:
    def __init__(self, layout, function, population_size=20, mutation_rate=0.1, crossover_rate=0.8, simulation_threshold=0.7, elite_size=3):
        self.base_layout = layout
        self.function = function
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.simulation_threshold = simulation_threshold
        self.elite_size = elite_size
        self.population = []
        self.generation = 0
        self.best_fitness_history = []
        self.builder = None

    def initialize_population(self):
        """Initialize the population using the Builder."""
        self.population = []
        self.builder = self.base_layout.builder
        self.builder.set_astar(astar)
        
        for _ in range(self.population_size):
            new_layout = copy.deepcopy(self.base_layout)
            if self.builder.randomize_layout():
                self.population.append(new_layout)
            else:
                # If we couldn't find a valid layout, use the base layout
                self.population.append(copy.deepcopy(self.base_layout))

    def crossover(self, parent1, parent2):
        """Create a child layout by combining two parents."""
        child = copy.deepcopy(parent1)
        for i, entity in enumerate(child.auto_placed_entities):
            if random.random() < 0.5:
                entity['position'] = parent2.auto_placed_entities[i]['position']
        
        # Repair the child layout
        builder = child.builder
        builder.set_astar(astar)
        if not builder.has_valid_paths():
            # If the child is invalid, return one of the parents
            return random.choice([parent1, parent2])
            
        return child

    def mutate(self, layout):
        """Mutate a layout by moving entities."""
        builder = layout.builder
        builder.set_astar(astar)
        
        for entity in layout.auto_placed_entities:
            if random.random() < self.mutation_rate:
                # Get available positions
                available = [pos for pos in builder.get_available_positions() 
                           if builder.is_position_valid(pos, entity)]
                
                if available:
                    # Try to find a valid position
                    for pos in random.sample(available, min(len(available), 5)):
                        old_pos = entity['position']
                        entity['position'] = pos
                        if builder.has_valid_paths():
                            break
                        else:
                            entity['position'] = old_pos

    def evaluate_fitness(self, layout):
        """Evaluate the fitness of a layout."""
        try:
            fitness = self.function(layout)
            return fitness if fitness is not None else -1
        except Exception as e:
            print(f"Error evaluating fitness: {e}")
            return -1

    def evolve(self):
        """Evolve the population for one generation."""
        # Evaluate all layouts
        scored_population = []
        for layout in self.population:
            fitness = self.evaluate_fitness(layout)
            scored_population.append((layout, fitness))
        
        # Sort by fitness (descending)
        scored_population.sort(key=lambda x: x[1], reverse=True)
        
        # Keep track of best fitness
        best_fitness = scored_population[0][1]
        self.best_fitness_history.append(best_fitness)
        
        # Select elites
        elites = [layout for layout, _ in scored_population[:self.elite_size]]
        
        # Create new population
        new_population = elites.copy()
        
        # Fill rest of population
        while len(new_population) < self.population_size:
            # Select parents using tournament selection
            tournament_size = 3
            tournament = random.sample(scored_population, tournament_size)
            parent1 = max(tournament, key=lambda x: x[1])[0]
            
            tournament = random.sample(scored_population, tournament_size)
            parent2 = max(tournament, key=lambda x: x[1])[0]
            
            # Crossover
            if random.random() < self.crossover_rate:
                child = self.crossover(parent1, parent2)
            else:
                child = copy.deepcopy(parent1)
            
            # Mutation
            self.mutate(child)
            
            new_population.append(child)
        
        self.population = new_population
        self.generation += 1

    def best_layouts(self, n=3):
        """Get the best n layouts from the current population."""
        scored_population = [(layout, self.evaluate_fitness(layout)) for layout in self.population]
        scored_population.sort(key=lambda x: x[1], reverse=True)
        return [layout for layout, score in scored_population[:n]]