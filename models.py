import random

class Layout:
    def __init__(self, width, length) -> None:
        self.length = length
        self.width = width
        self.aisle_width = 1  # Default aisle width
        self.builder = Builder(self)

        self.entities = []
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

        self.operations = {}
        
        for x in range(0, width + 2):
            self.structure['wall'].append((x, 0))
            self.structure['wall'].append((x, length + 1))

        for y in range(0, length + 1):
            self.structure['wall'].append((0, y))
            self.structure['wall'].append((width + 1, y))

    def get_fitness(self):
       return 0 
    
    def get_cell(x, y):
        result = []
        return 

    def add_structure(self, layout):
        for coord in layout.keys():
            self.structure[layout[coord]].append([int(n) for n in coord.split(',')])

    def add_zones(self, layout):
        for coord in layout.keys():
            self.zones[layout[coord]].append([int(n) for n in coord.split(',')])

    def add_utilities(self, layout):
        for coord in layout.keys():
            self.utilities[layout[coord]].append([int(n) for n in coord.split(',')])

    def add_entities(self, entities):
        id = 0
        for entity in entities:
            entity['entity_id'] = id
            # Set initial position for auto-placed entities
            if entity.get('placement') == 'auto':
                # Find available position
                available_positions = []
                for x in range(1, self.width + 1):
                    for y in range(1, self.length + 1):
                        pos = (x, y)
                        if (pos not in self.structure.get('wall', []) and 
                            pos not in self.structure.get('aisle', []) and
                            not any(e.get('position') == pos for e in self.entities)):
                            available_positions.append(pos)
                
                if available_positions:
                    entity['position'] = available_positions[0]  # Use first available position
                else:
                    # If no available positions, place at a random position
                    entity['position'] = (
                        random.randint(1, self.width),
                        random.randint(1, self.length)
                    )
            self.entities.append(entity)
            id += 1

    def add_operations(self, operations):
        id = 0
        for op in operations:
            op['operations_id'] = id
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
        return self.structure

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
    def __init__(self, from_entity, to_entity, frequency=1):
        self.from_entity = from_entity
        self.to_entity = to_entity
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
                
        return True

    def has_valid_paths(self):
        """Check if all operations have valid paths."""
        if not self.astar:
            raise ValueError("A* function not set")
            
        for operation in self.layout.operations:
            from_pos = operation.from_entity
            to_pos = operation.to_entity
            
            # Check if both positions are valid
            if not (self.is_position_valid(from_pos, {}) and 
                   self.is_position_valid(to_pos, {})):
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