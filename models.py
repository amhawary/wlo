import random
import copy

class Layout:
    def __init__(self, width, length) -> None:
        self.length = length
        self.width = width
        self.aisle_width = 1  # Default aisle width
        self.builder = Builder(self)

        self.entities = []
        self.operations = []  # Initialize operations as a list
        self.structure = {
            'wall':[],
            'loading':[],
            'ex':[],
            'ent':[],
            'ex_ent':[],
        }
        self.zones = {
            'highTemp':[],
            'lowTemp':[],
            'highHumidity':[],
            'lowHumidity':[],
        }
        self.utilities = {
    	    'gas': [],
    	    'electric': [],
    	    'water': [],
    	    'air': [],
    	    'earth': [],
    	    'network': [],
    	    'security': [],
        }

        self.operations = []

        for x in range(0, width + 2):
            pos1 = (x, 0)
            pos2 = (x, length + 1)
            self.structure['wall'].append(pos1)
            self.structure['wall'].append(pos2)

        for y in range(0, length + 1):
            pos1 = (0, y)
            pos2 = (width + 1, y)
            self.structure['wall'].append(pos1)
            self.structure['wall'].append(pos2)

    def add_structure(self, layout):
        for coord in layout.keys():
            pos = tuple([int(n) for n in coord.split(',')])
            entity_type = layout[coord]
            self.structure[entity_type].append(pos)
            if entity_type != "wall":
                self.add_entities([])

    def add_zones(self, layout):
        for coord in layout.keys():
            self.zones[layout[coord]].append([int(n) for n in coord.split(',')])

    def add_utilities(self, layout):
        for coord in layout.keys():
            self.utilities[layout[coord]].append([int(n) for n in coord.split(',')])

    def add_entities(self, entities):
        id = len(self.entities)
        for entity in entities:
                print(entity)
                print(entity["quantity"])
                for i in range (entity["quantity"]):
                    entity['id'] = id
                    self.entities.append(entity)
                    id += 1

    def add_operations(self, operations):
        id = len(self.operations)
        for op in operations:
            op['id'] = id
            self.operations.append(op)
            id += 1

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
        # Convert entities back to structure map for compatibility
        structure_map = {
            'wall': [],
            'loading': [],
            'ex': [],
            'ent': [],
            'ex_ent': [],
        }
        
        for entity in self.entities:
            if entity['category'] == 'structure':
                structure_map[entity['type']].append(entity['position'])
                
        return structure_map

    def getZoneMap():
        pass
    
    def getUtilitiesMap():
        pass
    
    def to_dict(self):
        return {
        'length': self.length,
        'width': self.width,
        'entities': self.entities,
        'structure': self.structure,
        'zones': self.zones,
        'utilities': self.utilities,
        'operations':self.operations
        }
    
    @classmethod
    def from_dict(cls, data):
        layout = cls(data['width'], data['length'])
        layout.entities = data['entities']
        layout.structure = data['structure']
        layout.zones = data['zones']
        layout.utilities = data['utilities']
        layout.operations = data['operations']

        return layout
    
class Operation:
    def __init__(self, from_entity, to_entity, frequency=1, id=None):
        self.id = id
        self.from_entity = from_entity
        self.to_entity = to_entity
        self.frequency = frequency

class Entity:
    def __init__(self, category, type_, placement, quantity, width, length, depends_on, within_zone, id=None):
        self.id = id
        self.category = category
        self.type = type_
        self.placement = placement
        self.quantity = quantity
        self.width = width
        self.length = length
        self.depends_on = depends_on
        self.within_zone = within_zone
        self.positions = []


class Builder:
    def __init__(self, layout) -> None:
        self.layout = layout
        self.astar = None  # Will be set by the caller

    def set_astar(self, astar_func):
        """Set the A* pathfinding function."""
        self.astar = astar_func

    def get_available_positions(self):
        """Get all available positions that are not walls, aisles, or occupied."""
        available = []
        for x in range(1, self.layout.width + 1):
            for y in range(1, self.layout.length + 1):
                pos = (x, y)
                if (pos not in self.layout.structure.get('wall', []) and 
                    not any(e.get('position') == pos for e in self.layout.entities)):
                    available.append(pos)
        return available

    def is_position_valid(self, pos, entity):
        """Check if a position is valid for an entity."""
        # Check if position is within bounds
        if not (1 <= pos[0] <= self.layout.width and 1 <= pos[1] <= self.layout.length):
            return False
            
        # Check if position is not a wall or aisle
        if (pos in self.layout.structure.get('wall', []) or 
            pos in self.layout.structure.get('aisle', [])):
            return False
            
        # Check if position is not occupied
        if any(e.get('position') == pos for e in self.layout.entities):
            return False
            
        # Check zone constraints if specified
        if entity.get('within_zone'):
            zone_type = entity['within_zone']
            if pos not in self.layout.zones.get(zone_type, []):
                return False

        # Check if at least one cell of the entity has access to an aisle
        # This is done by checking if any of the entity's cells has an adjacent aisle
        width = entity.get('width', 1)
        length = entity.get('length', 1)
        
        # Get all cells that would be occupied by this entity
        entity_cells = []
        for x in range(pos[0], pos[0] + width):
            for y in range(pos[1], pos[1] + length):
                entity_cells.append((x, y))
        
        # Check if any cell has access to an aisle
        has_access = False
        for cell in entity_cells:
            # Check adjacent cells (up, down, left, right)
            adjacent_cells = [
                (cell[0], cell[1] - 1),  # up
                (cell[0], cell[1] + 1),  # down
                (cell[0] - 1, cell[1]),  # left
                (cell[0] + 1, cell[1])   # right
            ]
            
            for adj_cell in adjacent_cells:
                # Check if adjacent cell is within bounds
                if not (1 <= adj_cell[0] <= self.layout.width and 1 <= adj_cell[1] <= self.layout.length):
                    continue
                
                # Check if adjacent cell is an aisle
                if adj_cell in self.layout.structure.get('aisle', []):
                    has_access = True
                    break
            
            if has_access:
                break
                
        if not has_access:
            return False
                
        return True

    def has_valid_paths(self):
        """Check if all operations have valid paths."""
        if not self.astar:
            raise ValueError("A* function not set")
            
        for operation in self.layout.operations:
            # Handle both coordinate-based and entity-based operations
            if isinstance(operation["from_entity"], tuple):
                # Coordinate-based operation
                from_pos = operation["from_entity"]
                to_pos = operation["to_entity"]
                # Create dummy entities for validation
                from_entity = {"width": 1, "length": 1}
                to_entity = {"width": 1, "length": 1}
            else:
                # Entity-based operation
                from_entity = next((e for e in self.layout.entities if e.get('id') == operation["from_entity"]), None)
                to_entity = next((e for e in self.layout.entities if e.get('id') == operation["to_entity"]), None)
                
                if not from_entity or not to_entity:
                    return False
                    
                from_pos = from_entity.get('position')
                to_pos = to_entity.get('position')
                
                if not from_pos or not to_pos:
                    return False
            
            # Check if both positions are valid
            if not (self.is_position_valid(from_pos, from_entity) and 
                   self.is_position_valid(to_pos, to_entity)):
                return False
                
            # Check if path exists
            path = self.astar(from_pos, to_pos, self.layout, self.layout.aisle_width)
            if not path:
                return False
                
        return True

    def randomize_layout(self):
        """Randomize the layout while respecting constraints."""
        if not self.astar:
            raise ValueError("A* function not set")
            
        # Get all auto-placed entities
        auto_entities = self.layout.auto_placed_entities
        
        # Try to find a valid layout
        max_attempts = 100
        for attempt in range(max_attempts):
            # Clear existing positions
            for entity in auto_entities:
                entity['position'] = None
                
            # Try to place each entity
            success = True
            for entity in auto_entities:
                # Get available positions that respect zone constraints
                available = [pos for pos in self.get_available_positions() 
                           if self.is_position_valid(pos, entity)]
                
                if not available:
                    success = False
                    break
                    
                # Randomly choose a position
                entity['position'] = random.choice(available)
                
            # If all entities placed, check if paths are valid
            if success and self.has_valid_paths():
                return True
                
        # If we couldn't find a valid layout after max attempts
        return False

    def crossover_layouts(self, parent1, parent2):
        """Create a child layout by combining two parents."""
        child = copy.deepcopy(parent1)
        
        # Get clusters from both parents
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
        
        # Validate and repair the child layout
        if not self.has_valid_paths():
            # Try to repair by adjusting cluster positions
            clusters = self._find_clusters(child)
            for cluster in clusters:
                # Try to move the entire cluster to a new valid location
                available = list(self.get_available_positions())
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
                    if not self.has_valid_paths():
                        for (i, entity), old_pos in zip(cluster, old_positions):
                            entity['position'] = old_pos
            
            # If still invalid after repairs, return one of the parents
            if not self.has_valid_paths():
                return random.choice([parent1, parent2])
        
        return child

    def mutate_layout(self, layout):
        """Mutate a layout by moving entities, preserving clusters when possible."""
        # Find existing clusters
        clusters = self._find_clusters(layout)
        
        # Mutation probabilities
        cluster_mutation_prob = 0.3  # Probability to mutate an entire cluster
        single_mutation_prob = 0.1   # Lower probability to mutate single entities
        
        # Try to mutate clusters first
        for cluster in clusters:
            if random.random() < cluster_mutation_prob:
                # Get all valid positions for the base entity
                available_positions = list(self.get_available_positions())
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
                if not self.has_valid_paths():
                    for (i, entity), old_pos in zip(cluster, old_positions):
                        entity['position'] = old_pos
        
        # Then try to mutate some individual entities
        for i, entity in enumerate(layout.auto_placed_entities):
            if random.random() < single_mutation_prob:
                available = [pos for pos in self.get_available_positions() 
                           if self.is_position_valid(pos, entity)]
                if available:
                    old_pos = entity['position']
                    entity['position'] = random.choice(available)
                    
                    if not self.has_valid_paths():
                        entity['position'] = old_pos

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

    def find_entity_access_point(self, entity_id):
        """Find the access point for a specific entity by its ID.
        
        Args:
            entity_id: The ID of the entity to find the access point for
            
        Returns:
            tuple: (access_point, adjacent_cell) where:
                - access_point is the cell of the entity that has access
                - adjacent_cell is the adjacent aisle cell that provides access
            Returns (None, None) if no access point is found
        """
        # Find the entity by ID
        entity = next((e for e in self.layout.entities if e.get('id') == entity_id), None)
        if not entity or not entity.get('position'):
            return None, None
            
        pos = entity['position']
        width = entity.get('width', 1)
        length = entity.get('length', 1)
        
        # Get all cells occupied by the entity
        entity_cells = []
        for x in range(pos[0], pos[0] + width):
            for y in range(pos[1], pos[1] + length):
                entity_cells.append((x, y))
        
        # Check each cell for access to an aisle
        for cell in entity_cells:
            # Check adjacent cells (up, down, left, right)
            adjacent_cells = [
                (cell[0], cell[1] - 1),  # up
                (cell[0], cell[1] + 1),  # down
                (cell[0] - 1, cell[1]),  # left
                (cell[0] + 1, cell[1])   # right
            ]
            
            for adj_cell in adjacent_cells:
                # Check if adjacent cell is within bounds
                if not (1 <= adj_cell[0] <= self.layout.width and 1 <= adj_cell[1] <= self.layout.length):
                    continue
                
                # Check if adjacent cell is an aisle
                if adj_cell in self.layout.structure.get('aisle', []):
                    return cell, adj_cell
        
        return None, None