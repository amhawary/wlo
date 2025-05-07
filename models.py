import random
import copy
from collections import deque

class Layout:
    def __init__(self, width, length) -> None:
        self.length = length
        self.width = width
        self.aisle_width = 1  # Default aisle width
        self.builder = Builder(self)
        self.fitness = 0
        self.entities = []
        self.operations = []
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
        
        for key in self.structure.keys():
            if key != 'wall':
                coords = self.structure[key]
                groups = group_touching_clusters(coords)
                id = len(self.entities)
                for group in groups:
                    self.entities.append({
                        'id':id,
                        'category':key,
                        'type':key,
                        'placement':'manual',
                        'quantity':1,
                        'width':1,
                        'length':1,
                        'depends_on':'none',
                        'within_zone':'none',
                        'positions':group
                        })
                    id+=1

    def add_zones(self, layout):
        for coord in layout.keys():
            self.zones[layout[coord]].append([int(n) for n in coord.split(',')])

    def add_utilities(self, layout):
        for coord in layout.keys():
            self.utilities[layout[coord]].append([int(n) for n in coord.split(',')])

    def add_entities(self, entities):
        id = len(self.entities)
        for entity in entities:
            for i in range(entity["quantity"]):
                new_entity = entity.copy()  # Create a shallow copy
                new_entity['id'] = id
                new_entity['positions'] = []
                self.entities.append(new_entity)
                id += 1

    def add_operations(self, operations):
        id = len(self.operations)
        for op in operations:
            new_op = op.copy()
            new_op['id'] = id
            new_op['from_entity']={'id':op['from_entity'], 'positions':self.entities[int(op['from_entity'])]['positions']}
            new_op['to_entity']={'id':op['to_entity'], 'positions':self.entities[int(op['to_entity'])]['positions']}
            self.operations.append(new_op)
            id += 1

    def add_positions(self, layout):
        for coord in layout.keys():
            self.entities[int(layout[coord])]['positions'].append([int(n) for n in coord.split(',')])
    
    def delete_positions(self):
        for entity in self.entities:
            if entity['placement'] == 'auto':
                entity['positions'] = []

    def refresh_operations(self):
        operations_copy = self.operations
        self.operations = []
        for op in operations_copy:
            new_op = op.copy()
            new_op['id'] = op['id']
            new_op['from_entity']={'id':op['from_entity']['id'], 'positions':self.entities[int(op['from_entity']['id'])]['positions']}
            new_op['to_entity']={'id':op['to_entity']['id'], 'positions':self.entities[int(op['to_entity']['id'])]['positions']}
            self.operations.append(new_op)

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
        """Get all available positions that are not walls or occupied."""
        available = []
        for x in range(1, self.layout.width + 1):
            for y in range(1, self.layout.length + 1):
                pos = (x, y)
                if (pos not in self.layout.structure.get('wall', []) and 
                    not any(p == pos for e in self.layout.entities for p in e.get('positions'))):
                    available.append(pos)
        return available

    def is_position_valid(self, pos, entity):
        """Check if a position is valid for an entity."""
        # Check if position is within bounds
        if not (1 <= pos[0] <= self.layout.width and 1 <= pos[1] <= self.layout.length):
            return False
            
        # Check zone constraints if specified
        if entity.get('within_zone') != 'none':
            zone_type = entity['within_zone']
            if pos not in self.layout.zones.get(zone_type, []):
                return False

        width = entity.get('width', 1)
        length = entity.get('length', 1)
        
        # Get all cells that would be occupied by this entity
        entity_cells = []
        for x in range(pos[0], pos[0] + width):
            for y in range(pos[1], pos[1] + length):
                entity_cells.append((x, y))

        new_entity = copy.deepcopy(entity)
        new_entity['positions'] =  entity_cells
        # Check if any cell has access to an aisle
        if not self.has_access_point(new_entity):
            return False

        return True

    def has_valid_paths(self):
        """Check if all operations have valid paths."""
        if not self.astar:
            raise ValueError("A* function not set")
            
        for operation in self.layout.operations:
            temp_paths = []
            from_coords = operation['from_entity']['positions']
            to_coords = operation['to_entity']['positions']
            for to_coord in to_coords:
                for from_coord in from_coords:
                    path = self.astar(from_coord, to_coord, self.layout, self.layout.aisle_width)
                    if path:
                        temp_paths.append(path)
            if temp_paths == []:
                return False

        return True

    def randomise_layout(self):
        """Randomise the layout while respecting constraints."""
        if not self.astar:
            raise ValueError("A* function not set")
            
        # Get all auto-placed entities
        auto_entities = self.layout.auto_placed_entities

        # Try to find a valid layout
        max_attempts = 100
        for attempt in range(max_attempts):
            # Try to place each entity
            success = True
            self.layout.delete_positions()

            random.shuffle(auto_entities)
            for entity in auto_entities:
                # Get available positions that respect zone constraints
                available = []
                for pos in self.get_available_positions():
                    if self.is_position_valid(pos, entity):
                        available.append(pos)
                
                if not available:
                    success = False
                    break
                    
                # Randomly choose a position
                pos = random.choice(available)
                entity_cells = []
                for x in range(pos[0], pos[0] + entity['width']):
                    for y in range(pos[1], pos[1] + entity['length']):
                        entity_cells.append((x, y))
                
                positions = {}
                for e in entity_cells:
                    positions[str(e)[1:-1]] = entity['id']
                
                self.layout.add_positions(positions)
            self.layout.refresh_operations()

            # If all entities placed, check if paths are valid
            if success and self.has_valid_paths():
                return True
        
        # If we couldn't find a valid layout after max attempts
        return False

    def has_access_point(self, entity):
        # Check each cell for access to an aisle
        for cell in entity.get('positions'):
            # Check adjacent cells (up, down, left, right)
            adjacent_cells = [
                (cell[0], cell[1] - 1),  # up
                (cell[0], cell[1] + 1),  # down
                (cell[0] - 1, cell[1]),  # left
                (cell[0] + 1, cell[1])   # right
            ]
            
            all_empty_cells = self.get_available_positions()
            for adj_cell in adjacent_cells:
                # Check if adjacent cell is within bounds
                if adj_cell in all_empty_cells:
                    return True
                
        return False
    
# more helpers
    
def group_touching_clusters(coords):
    coords_set = set(coords)  # For O(1) lookups
    visited = set()
    clusters = []

    # 8 directions (horizontal, vertical, diagonal)
    directions = [(-1,  0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for coord in coords:
        if coord in visited:
            continue

        cluster = []
        queue = deque([coord])
        visited.add(coord)

        while queue:
            current = queue.popleft()
            cluster.append(current)

            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in coords_set and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        clusters.append(cluster)

    return clusters