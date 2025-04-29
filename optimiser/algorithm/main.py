# main.py

from gasim import Gasim
from layout import Layout, Operation  # adjust import names

def print_layout(layout):
    grid = [[' ' for _ in range(layout.width + 2)] for _ in range(layout.length + 2)]

    # Walls
    for (x, y) in layout.structure.get('wall', []):
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = '#'

    # Aisles
    for (x, y) in layout.structure.get('aisle', []):
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = '.'

    # Entities
    for entity in layout.entities:
        pos = entity.get('position')
        if pos:
            x, y = pos
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                # Use first letter of entity type
                grid[y][x] = entity['type'][0].upper()

    # Print the grid
    for row in grid:
        print(' '.join(row))

# 1. Setup Layout
layout = Layout(width=10, length=10)

# Add some dummy entities
layout.addEntities([
    {"type": "itemA", "placement": "auto", "size": (1,1)},
    {"type": "itemA", "placement": "auto", "size": (1,1)},
    {"type": "itemB", "placement": "auto", "size": (1,1)},
    {"type": "itemC", "placement": "auto", "size": (1,1)},
    {"type": "itemC", "placement": "auto", "size": (1,1)},
    {"type": "itemC", "placement": "auto", "size": (1,1)},
    {"type": "itemC", "placement": "auto", "size": (1,1)},
    {"type": "itemC", "placement": "auto", "size": (1,1)},
    {"type": "itemC", "placement": "auto", "size": (1,1)},
])

# 2. Setup Operations
operations = [
    Operation((2,2), (8,8), frequency=5),
    Operation((5,5), (1,1), frequency=3),
]
# Dummy simulation object (since you don't have one yet)
class DummySim:
    def __init__(self, operations):
        self.operations = operations

    def simulate(self, layout):
        return layout.get_fitness(self.operations)  # fallback to static metrics

simulation = DummySim(operations)

# 3. Initialize and run Gasim
gasim = Gasim(layout, simulation, population_size=10)
gasim.initialize_population()

for i in range(20):  # 20 generations
    gasim.evolve()
    print(f"Generation {i+1} done.")

# 4. Get best layouts
best_layouts = gasim.best_layouts()

for b in best_layouts:

    print_layout(b)

print("Top Layouts Fitness:")
for i, l in enumerate(best_layouts):
    fitness = l.get_fitness(simulation.operations)
    print(f"Layout {i+1}: Fitness = {fitness:.4f}")
