# gasim = Genetic Algorithm + Simulation

import math

class Gasim:
    def __init__(self, layout, simulation, population_size=30, generations=50, sim_threshold=0.8):
        self.layout = layout
        self.simulation = simulation
        self.population_size = population_size
        self.generations = generations
        self.sim_threshold = sim_threshold
        self.population = [layout * population_size]
        self.fitness_scores = []

    def _euclidean(self, a, b):
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def _normalise(self, value, min_val, max_val):
        if max_val == min_val:
            return 0
        return (value - min_val) / (max_val - min_val)

    def _calculate_coi(self):
        total_volume = 0
        for entity in self.layout.entities:
            if 'size' in entity:
                total_volume += entity['size'][0] * entity['size'][1]
        orders = max(len(self.layout.entities), 1)
        return total_volume / orders

    def _diagonal_and_cross_score(self):
        aisles = self.layout.structure.get('aisle', [])
        diagonal_count = 0
        cross_points = set()
        horiz_aisles = set()
        vert_aisles = set()

        for x, y in aisles:
            if (x+1, y+1) in aisles or (x-1, y-1) in aisles or (x+1, y-1) in aisles or (x-1, y+1) in aisles:
                diagonal_count += 1
            if (x+1, y) in aisles or (x-1, y) in aisles:
                horiz_aisles.add((x, y))
            if (x, y+1) in aisles or (x, y-1) in aisles:
                vert_aisles.add((x, y))

        cross_points = horiz_aisles & vert_aisles
        if not aisles:
            return 0
        return 0.5 * (diagonal_count / len(aisles)) + 0.5 * (len(cross_points) / len(aisles))

    def _similar_item_clustering_score(self):
        similar_pairs = []
        max_dist = math.sqrt(self.layout.width**2 + self.layout.length**2)

        for i in range(len(self.layout.entities)):
            for j in range(i + 1, len(self.layout.entities)):
                if self.layout.entities[i]['type'] == self.layout.entities[j]['type']:
                    dist = self._euclidean(self.layout.entities[i]['position'], self.layout.entities[j]['position'])
                    similar_pairs.append(dist)

        if not similar_pairs:
            return 1
        avg_dist = sum(similar_pairs) / len(similar_pairs)
        return 1 - (avg_dist / max_dist)

    def _operation_travel_score(self, operations):
        total_distance = 0
        total_freq = 0
        for op in operations:
            d = self._euclidean(op.from_coords, op.to_coords)
            total_distance += d * op.frequency
            total_freq += op.frequency
        if total_freq == 0:
            return 1
        avg = total_distance / total_freq
        max_dist = math.sqrt(self.layout.width**2 + self.layout.length**2)
        return 1 - (avg / max_dist)

    def calculate_fitness(self, operations):
        turnover = 20  # placeholder
        throughput = 250  # placeholder
        coi = self._calculate_coi()

        t_norm = self._normalise(turnover, 10, 50)
        p_norm = self._normalise(throughput, 100, 500)
        coi_norm = self._normalise(coi, 0.1, 1.0)

        aisle_score = self._diagonal_and_cross_score()
        clustering = self._similar_item_clustering_score()
        op_score = self._operation_travel_score(operations)

        weights = [0.15, 0.15, 0.15, 0.2, 0.2, 0.15]  # turnover, throughput, COI, aisle, cluster, op
        fitness = (
            weights[0] * t_norm +
            weights[1] * p_norm +
            weights[2] * (1 - coi_norm) +
            weights[3] * aisle_score +
            weights[4] * clustering +
            weights[5] * op_score
        )
        return fitness

    def run_evolution(self, operations):
        # Placeholder: Add GA evolution logic here, store top candidates
        best_candidates = []  # fill this with tuples of (layout, fitness)
        return best_candidates

    def simulate_top_layouts(self, top_layouts):
        # Placeholder: Simulate and rank
        simulated_results = []
        for layout in top_layouts:
            result = self.simulation.run(layout)
            simulated_results.append((layout, result))
        simulated_results.sort(key=lambda x: x[1], reverse=True)
        return simulated_results[:3]  # top 3 layouts for user selection
 