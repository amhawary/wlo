# gasim.py

import random
import copy
import math

class Gasim:
    def __init__(self, layout, simulation, population_size=20, mutation_rate=0.1, crossover_rate=0.8, simulation_threshold=0.7, elite_size=3):
        self.base_layout = layout
        self.simulation = simulation
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.simulation_threshold = simulation_threshold
        self.elite_size = elite_size
        self.population = []
        self.generation = 0

    def initialize_population(self):
        self.population = []
        for _ in range(self.population_size):
            new_layout = copy.deepcopy(self.base_layout)
            self.randomize_layout(new_layout)
            self.population.append(new_layout)

    def randomize_layout(self, layout):
        for entity in layout.autoPlacedEntities:
            entity['position'] = (
                random.randint(1, layout.width),
                random.randint(1, layout.length)
            )

    def crossover(self, parent1, parent2):
        child = copy.deepcopy(parent1)
        for i, entity in enumerate(child.entities):
            if entity['placement'] == 'auto':
                if random.random() < 0.5:
                    entity['position'] = parent2.entities[i]['position']
        self.repair(child)
        return child

    def mutate(self, layout):
        for entity in layout.autoPlacedEntities:
            if random.random() < self.mutation_rate:
                # Small random move
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])
                new_x = max(1, min(layout.width, entity['position'][0] + dx))
                new_y = max(1, min(layout.length, entity['position'][1] + dy))
                entity['position'] = (new_x, new_y)

    def repair(self, layout):
        # Simple repair: prevent overlapping by moving duplicates
        seen = set()
        for entity in layout.autoPlacedEntities:
            while entity['position'] in seen:
                entity['position'] = (
                    random.randint(1, layout.width),
                    random.randint(1, layout.length)
                )
            seen.add(entity['position'])

    def evaluate_fitness(self, layout):
        if self.generation / 100 > self.simulation_threshold:
            return self.simulation.simulate(layout)  # hypothetical
        else:
            return layout.get_fitness(self.simulation.operations)

    def evolve(self):
        scored_population = [(layout, self.evaluate_fitness(layout)) for layout in self.population]
        scored_population.sort(key=lambda x: x[1], reverse=True)

        elites = [layout for layout, _ in scored_population[:self.elite_size]]

        new_population = elites.copy()

        while len(new_population) < self.population_size:
            parent1, parent2 = random.choices(scored_population, weights=[s for _, s in scored_population], k=2)
            if random.random() < self.crossover_rate:
                child = self.crossover(parent1[0], parent2[0])
            else:
                child = copy.deepcopy(parent1[0])

            self.mutate(child)
            new_population.append(child)

        self.population = new_population
        self.generation += 1

    def best_layouts(self, n=3):
        scored_population = [(layout, self.evaluate_fitness(layout)) for layout in self.population]
        scored_population.sort(key=lambda x: x[1], reverse=True)
        return [layout for layout, score in scored_population[:n]]