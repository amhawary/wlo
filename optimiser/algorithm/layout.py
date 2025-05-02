import math
from collections import defaultdict

class Operation:
    def __init__(self, from_entity, to_entity, frequency=1):
        self.from_coords = from_entity
        self.to_coords = to_entity
        self.frequency = frequency

class Entity:
    def __init__(self, category, type_, placement, quantity, depends_on, within_zone, facing_direction):
        self.category = category
        self.type = type_
        self.placement = placement
        self.quantity = quantity
        self.depends_on = depends_on
        self.within_zone = within_zone
        self.facing_direction = facing_direction
        self.positions = []

class Layout:
    def __init__(self, width, length) -> None:
        self.length = length
        self.width = width
        self.entities = []
        self.structure = {
            'wall': [],
            'loading': [],
            'ex': [],
            'ent': [],
            'ex_ent': [],
        }
        self.zones = {
            'highTemp': [],
            'lowTemp': [],
            'highHumidity': [],
            'lowHumidity': [],
        }
        self.utilities = defaultdict(list)

        for x in range(0, width + 2):
            self.structure['wall'].append((x, 0))
            self.structure['wall'].append((x, length + 1))
        for y in range(0, length + 1):
            self.structure['wall'].append((0, y))
            self.structure['wall'].append((width + 1, y))

    def _euclidean(self, a, b):
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def _normalize(self, value, min_val, max_val):
        if max_val == min_val:
            return 0
        return (value - min_val) / (max_val - min_val)

    def _calculate_coi(self):
        total_volume = 0
        for entity in self.entities:
            if hasattr(entity, 'size'):
                total_volume += entity.size[0] * entity.size[1]
        orders = max(len(self.entities), 1)
        return total_volume / orders
   
    def _diagonal_and_cross_score(self):
        # Aisle = all empty positions
        filled = set(self.structure['wall'])
        for entity in self.entities:
            filled.update(entity.positions)

        aisles = [
            (x, y)
            for x in range(1, self.width + 1)
            for y in range(1, self.length + 1)
            if (x, y) not in filled
        ]

        diagonal_count = 0
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
        score = 0.5 * (diagonal_count / len(aisles)) + 0.5 * (len(cross_points) / len(aisles))
        return score

    def _similar_item_clustering_score(self):
        similar_pairs = []
        max_dist = math.sqrt(self.width**2 + self.length**2)

        for i in range(len(self.entities)):
            for j in range(i + 1, len(self.entities)):
                if self.entities[i].type == self.entities[j].type:
                    if self.entities[i].positions and self.entities[j].positions:
                        dist = self._euclidean(self.entities[i].positions[0], self.entities[j].positions[0])
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
        max_dist = math.sqrt(self.width**2 + self.length**2)
        return 1 - (avg / max_dist)

    def get_fitness(self, operations):
        turnover = 20  # placeholder
        throughput = 250  # placeholder
        coi = self._calculate_coi()

        t_norm = self._normalize(turnover, 10, 50)
        p_norm = self._normalize(throughput, 100, 500)
        coi_norm = self._normalize(coi, 0.1, 1.0)

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


    def add_entities(self, entities):
        id = 0
        for entity in entities:
            entity["entity_id"] = id
            entity.setdefault('position', (0, 0))  # Default position if missing
            self.entities.append(entity)
            id += 1

    def clone(self):
        """
        Creates a deep copy of the layout (for GA crossover/mutation).
        """
        new_layout = Layout(self.width, self.length)
        new_layout.entities = [dict(entity) for entity in self.entities]
        new_layout.structure = {k: list(v) for k, v in self.structure.items()}
        new_layout.zones = {k: list(v) for k, v in self.zones.items()}
        new_layout.utilities = defaultdict(list, {k: list(v) for k, v in self.utilities.items()})
        return new_layout


    @property
    def auto_placed_entities(self):
        res = [] 
        for entity in self.entities:
            if entity['placement'] == 'auto':
                res.append(entity)
        return res
    
    @property
    def manual_placed_entities(self):
        res = [] 
        for entity in self.entities:
            if entity['placement'] == 'manual':
                res.append(entity)
        return res

    def getStructureMap(self):
        return self.structure

    def getZoneMap():
        pass
    
    def getUtilitiesMap():
        pass
    
    def to_dict(self):
        return {
        "length": self.length,
        "width": self.width,
        "entities": self.entities,
        "structure": self.structure,
        "zones": self.zones,
        "utilities": self.utilities
        }
    
    @classmethod
    def from_dict(cls, data):
        layout = cls(data["width"], data["length"])
        layout.entities = data['entities']
        layout.structure = data['structure']
        layout.zones = data['zones']
        layout.utilities = data['utilities']

        return layout
    
# class Layout:
#     def __init__(self, width, length) -> None:
#         self.length = length
#         self.width = width

#         self.entities = []
#         self.structure = {
#             'wall': [],
#             'aisle': [],
#             'loading': [],
#             'ex': [],
#             'ent': [],
#             'ex_ent': [],
#         }
#         self.zones = {
#             'highTemp': [],
#             'lowTemp': [],
#             'highHumidity': [],
#             'lowHumidity': [],
#         }
#         self.utilities = defaultdict(list)

#         for x in range(0, width + 2):
#             self.structure['wall'].append((x, 0))
#             self.structure['wall'].append((x, length + 1))
#         for y in range(0, length + 1):
#             self.structure['wall'].append((0, y))
#             self.structure['wall'].append((width + 1, y))

#     def _euclidean(self, a, b):
#         return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

#     def _normalize(self, value, min_val, max_val):
#         if max_val == min_val:
#             return 0
#         return (value - min_val) / (max_val - min_val)

#     def _calculate_coi(self):
#         total_volume = 0
#         for entity in self.entities:
#             if 'size' in entity:
#                 total_volume += entity['size'][0] * entity['size'][1]
#         orders = max(len(self.entities), 1)
#         return total_volume / orders

#     def _diagonal_and_cross_score(self):
#         aisles = self.structure.get('aisle', [])
#         diagonal_count = 0
#         horiz_aisles = set()
#         vert_aisles = set()

#         for x, y in aisles:
#             if (x+1, y+1) in aisles or (x-1, y-1) in aisles or (x+1, y-1) in aisles or (x-1, y+1) in aisles:
#                 diagonal_count += 1
#             if (x+1, y) in aisles or (x-1, y) in aisles:
#                 horiz_aisles.add((x, y))
#             if (x, y+1) in aisles or (x, y-1) in aisles:
#                 vert_aisles.add((x, y))

#         cross_points = horiz_aisles & vert_aisles
#         score = 0.5 * (diagonal_count / len(aisles)) + 0.5 * (len(cross_points) / len(aisles)) if aisles else 0
#         return score

#     def _similar_item_clustering_score(self):
#         similar_pairs = []
#         max_dist = math.sqrt(self.width**2 + self.length**2)

#         for i in range(len(self.entities)):
#             for j in range(i + 1, len(self.entities)):
#                 if self.entities[i]['type'] == self.entities[j]['type']:
#                     dist = self._euclidean(self.entities[i]['position'], self.entities[j]['position'])
#                     similar_pairs.append(dist)

#         if not similar_pairs:
#             return 1
#         avg_dist = sum(similar_pairs) / len(similar_pairs)
#         return 1 - (avg_dist / max_dist)

#     def _operation_travel_score(self, operations):
#         total_distance = 0
#         total_freq = 0
#         for op in operations:
#             d = self._euclidean(op.from_coords, op.to_coords)
#             total_distance += d * op.frequency
#             total_freq += op.frequency
#         if total_freq == 0:
#             return 1
#         avg = total_distance / total_freq
#         max_dist = math.sqrt(self.width**2 + self.length**2)
#         return 1 - (avg / max_dist)

#     def get_fitness(self, operations):
#         turnover = 20  # placeholder
#         throughput = 250  # placeholder
#         coi = self._calculate_coi()

#         t_norm = self._normalize(turnover, 10, 50)
#         p_norm = self._normalize(throughput, 100, 500)
#         coi_norm = self._normalize(coi, 0.1, 1.0)

#         aisle_score = self._diagonal_and_cross_score()
#         clustering = self._similar_item_clustering_score()
#         op_score = self._operation_travel_score(operations)

#         weights = [0.15, 0.15, 0.15, 0.2, 0.2, 0.15]  # turnover, throughput, COI, aisle, cluster, op
#         fitness = (
#             weights[0] * t_norm +
#             weights[1] * p_norm +
#             weights[2] * (1 - coi_norm) +
#             weights[3] * aisle_score +
#             weights[4] * clustering +
#             weights[5] * op_score
#         )
#         return fitness
