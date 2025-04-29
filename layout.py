class Layout:
    def __init__(self, width, length) -> None:
        self.length = length
        self.width = width

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

    def addStructure(self, layout):
        for coord in layout.keys():
            self.structure[layout[coord]].append([int(n) for n in coord.split(',')])

    def addZones(self, layout):
        for coord in layout.keys():
            self.zones[layout[coord]].append([int(n) for n in coord.split(',')])

    def addUtilities(self, layout):
        for coord in layout.keys():
            self.utilities[layout[coord]].append([int(n) for n in coord.split(',')])


    def addEntities(self, entities):
        id = 0
        for entity in entities:
            entity['entity_id'] = id
            self.entities.append(entity)
            id += 1
    
    @property
    def autoPlacedEntities(self):
        res = [] 
        for entity in self.entities:
            if entity['placement'] == 'auto':
                res.append(entity)
        return res
    
    @property
    def manualPlacedEntities(self):
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
        'utilities': self.utilities
        }
    
    @classmethod
    def from_dict(cls, data):
        layout = cls(data['width'], data['length'])
        layout.entities = data['entities']
        layout.structure = data['structure']
        layout.zones = data['zones']
        layout.utilities = data['utilities']

        return layout
    
class Operation:
    def __init__(self) -> None:
        pass