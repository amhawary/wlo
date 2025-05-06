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

    def _find_clusters(self, layout):
        """Find clusters of entities based on type and proximity."""
        clusters = []
        used_entities = set()
        
        # Parameters for clustering
        proximity_threshold = 3  # Maximum distance between entities in a cluster
        
        for i, entity in enumerate(layout.auto_placed_entities):
            if i in used_entities:
                continue
            
            # Start a new cluster
            cluster = [(i, entity)]
            used_entities.add(i)
            
            # Find nearby entities of the same type
            for j, other in enumerate(layout.auto_placed_entities):
                if j in used_entities:
                    continue
                
                if entity['type'] == other['type']:
                    pos1 = entity['position']
                    pos2 = other['position']
                    distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                    
                    if distance <= proximity_threshold:
                        cluster.append((j, other))
                        used_entities.add(j)
            
            clusters.append(cluster)
        
        return clusters

    def crossover(self, parent1, parent2):
        """Create a child layout by combining two parents using cluster-aware crossover."""
        child = copy.deepcopy(parent1)
        
        # Find clusters in both parents
        parent1_clusters = self._find_clusters(parent1)
        parent2_clusters = self._find_clusters(parent2)
        
        # Crossover probabilities
        cluster_swap_prob = 0.7  # High probability to swap entire clusters
        single_entity_prob = 0.1  # Low probability to swap single entities
        
        # Try to swap clusters first
        for cluster in parent1_clusters:
            if random.random() < cluster_swap_prob:
                # Find a matching cluster in parent2 (same entity types)
                cluster_type = cluster[0][1]['type']
                matching_clusters = [c for c in parent2_clusters 
                                  if c[0][1]['type'] == cluster_type]
                
                if matching_clusters:
                    # Swap positions with a random matching cluster
                    parent2_cluster = random.choice(matching_clusters)
                    for (i1, e1), (i2, e2) in zip(cluster, parent2_cluster):
                        child.auto_placed_entities[i1]['position'] = e2['position']
        
        # Then maybe swap some individual entities
        for i, entity in enumerate(child.auto_placed_entities):
            if random.random() < single_entity_prob:
                # Find entities of the same type in parent2
                same_type = [(j, e) for j, e in enumerate(parent2.auto_placed_entities)
                            if e['type'] == entity['type']]
                if same_type:
                    j, other = random.choice(same_type)
                    child.auto_placed_entities[i]['position'] = other['position']
        
        # Repair the child layout
        builder = child.builder
        builder.set_astar(astar)
        if not builder.has_valid_paths():
            # Try to repair by adjusting cluster positions
            clusters = self._find_clusters(child)
            for cluster in clusters:
                # Try to move the entire cluster to a new valid location
                available = list(builder.get_available_positions())
                if available:
                    base_pos = random.choice(available)
                    old_positions = []
                    
                    # Move all entities in cluster relative to the new base position
                    for i, entity in cluster:
                        old_positions.append(entity['position'])
                        dx = entity['position'][0] - cluster[0][1]['position'][0]
                        dy = entity['position'][1] - cluster[0][1]['position'][1]
                        new_x = base_pos[0] + dx
                        new_y = base_pos[1] + dy
                        
                        if 0 <= new_x < child.width and 0 <= new_y < child.length:
                            entity['position'] = (new_x, new_y)
                    
                    # If still invalid, revert the cluster
                    if not builder.has_valid_paths():
                        for (i, entity), old_pos in zip(cluster, old_positions):
                            entity['position'] = old_pos
            
            # If still invalid after repairs, return one of the parents
            if not builder.has_valid_paths():
                return random.choice([parent1, parent2])
        
        return child

    def mutate(self, layout):
        """Mutate a layout by moving entities, preserving clusters when possible."""
        builder = layout.builder
        builder.set_astar(astar)
        
        # Find existing clusters
        clusters = self._find_clusters(layout)
        
        # Mutation probabilities
        cluster_mutation_prob = 0.3  # Probability to mutate an entire cluster
        single_mutation_prob = 0.1   # Lower probability to mutate single entities
        
        # Try to mutate clusters first
        for cluster in clusters:
            if random.random() < cluster_mutation_prob:
                # Get all valid positions for the base entity
                available_positions = list(builder.get_available_positions())
                if not available_positions:
                    continue
                
                # Save old positions in case we need to revert
                old_positions = []
                base_pos = random.choice(available_positions)
                
                # Move all entities in cluster relative to the new base position
                for i, entity in cluster:
                    old_positions.append(entity['position'])
                    dx = entity['position'][0] - cluster[0][1]['position'][0]
                    dy = entity['position'][1] - cluster[0][1]['position'][1]
                    new_x = base_pos[0] + dx
                    new_y = base_pos[1] + dy
                    
                    if 0 <= new_x < layout.width and 0 <= new_y < layout.length:
                        entity['position'] = (new_x, new_y)
                
                # If the new positions make the layout invalid, revert
                if not builder.has_valid_paths():
                    for (i, entity), old_pos in zip(cluster, old_positions):
                        entity['position'] = old_pos
        
        # Then try to mutate some individual entities
        for i, entity in enumerate(layout.auto_placed_entities):
            if random.random() < single_mutation_prob:
                available = [pos for pos in builder.get_available_positions() 
                           if builder.is_position_valid(pos, entity)]
                if available:
                    old_pos = entity['position']
                    entity['position'] = random.choice(available)
                    
                    if not builder.has_valid_paths():
                        entity['position'] = old_pos

    def evaluate_fitness(self, layout):
        """Evaluate the fitness of a layout and return both total fitness and individual metrics."""
        try:
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
        except Exception as e:
            print(f"Error evaluating fitness: {e}")
            return -1, {}

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
    

    def run_optimisation(self):
        pass