import random
import copy
import math
from .__helpers import astar
from ..function.standard_layout_fitness import get_fitness

class GA:
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

        # Add new tracking attributes
        self.generation_fitness_metrics = []  # List of dictionaries for each generation
        self.current_generation_metrics = []  # List of individual metrics for current generation

    def init_population(self):
        """Initialize the population using the Builder."""
        self.population = []
        self.builder = self.base_layout.builder
        self.builder.set_astar(astar)
        
        for _ in range(self.population_size):
            new_layout = copy.deepcopy(self.base_layout)
            if self.builder.randomise_layout():
                self.population.append(new_layout)
            else:
                # If we couldn't find a valid layout, use the base layout
                self.population.append(copy.deepcopy(self.base_layout))
    
    def crossover(self, parent1, parent2):
        """Create a child layout by crossing over two parents."""
        child = copy.deepcopy(parent1)
        child.delete_positions()

        auto_entities = child.auto_placed_entities
        random.shuffle(auto_entities)

        for entity in auto_entities:
            # Choose entity shape from fitter parent
            source = parent1 if random.random() < 0.5 else parent2
            if entity['id'] in source.entities:
                entity_data = source.entities[entity['id']]
                entity['width'] = entity_data['width']
                entity['length'] = entity_data['length']

            # Get available positions that respect constraints
            available = []
            for pos in child.builder.get_available_positions():
                if child.builder.is_position_valid(pos, entity):
                    available.append(pos)

            if not available:
                return parent1 if (parent1.fitness or 0) >= (parent2.fitness or 0) else parent2

            # Choose random valid position
            pos = random.choice(available)
            entity_cells = []
            for x in range(pos[0], pos[0] + entity['width']):
                for y in range(pos[1], pos[1] + entity['length']):
                    entity_cells.append((x, y))

            positions = {}
            for e in entity_cells:
                positions[str(e)[1:-1]] = entity['id']

            child.add_positions(positions)

        child.refresh_operations()

        if child.builder.has_valid_paths():
            return child

        # Fallback if no valid paths
        return parent1 if (parent1.fitness or 0) >= (parent2.fitness or 0) else parent2

    def mutate(self, layout):
        return layout

    def evaluate_fitness(self, layout):
        """Evaluate the fitness of a layout and return both total fitness and individual metrics."""
        fitness = self.function(layout)
        if fitness is None:
            return -1, {}
        
        # Get individual metrics (assuming the function returns a tuple of (total_fitness, metrics_dict))
        if isinstance(fitness, tuple):
            total_fitness, metrics = fitness
        else:
            total_fitness = fitness
            metrics = {'total_fitness': fitness}
        
        return total_fitness, metrics

    def evolve(self):
        """Evolve the population for one generation."""
        # Reset current generation metrics
        self.current_generation_metrics = []
        
        # Evaluate all layouts
        scored_population = []
        for layout in self.population:
            fitness, metrics = self.evaluate_fitness(layout)
            scored_population.append((layout, fitness))
            self.current_generation_metrics.append(metrics)
        
        # Store metrics for this generation
        self.generation_fitness_metrics.append(self.current_generation_metrics)
        
        # Sort by fitness (descending)
        scored_population.sort(key=lambda x: x[1], reverse=True)
        
        # Keep track of best fitness
        best_fitness = scored_population[0][1]
        self.best_fitness_history.append(best_fitness)
        
        # Select elites
        elites = [layout for layout, _ in scored_population[:self.elite_size]]
        
        # Create new population
        new_population = elites.copy()

        print('Best Fitness is', best_fitness)
        
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

    def get_fitness_metrics(self):
        """Return the fitness metrics for all generations."""
        return self.generation_fitness_metrics

    def get_current_generation_metrics(self):
        """Return the fitness metrics for the current generation."""
        return self.current_generation_metrics
    

    def run(self):
        self.init_population()

        for i in range(25):  # 20 generations
            self.evolve()
            print(f"Generation {i+1} done.")

        best_layouts = self.best_layouts()
        
        self.layout1=best_layouts[0].to_dict()
        self.layout2=best_layouts[1].to_dict()
        self.layout3=best_layouts[2].to_dict()




