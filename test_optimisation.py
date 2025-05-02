from models import Layout, Operation
from optimiser.algorithm.gasim import Gasim
from optimiser.function.standard_layout_fitness import get_fitness

def print_layout(layout):
    """Print a visual representation of the layout."""
    #print("Creating grid...")  # Debug print
    grid = [[' ' for _ in range(layout.width + 2)] for _ in range(layout.length + 2)]
    
    #print("Adding walls...")  # Debug print
    # Add walls
    for (x, y) in layout.structure.get('wall', []):
        #print(f"Wall at {x}, {y}")  # Debug print
        if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
            grid[y][x] = '#'
    
    #print("Adding entities...")  # Debug print
    # Add entities
    for entity in layout.entities:
        pos = entity.get('position')
        #print(f"Entity {entity['type']} at {pos}")  # Debug print
        if pos:
            x, y = pos
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = entity['type'][0].upper()
    
    # Print the grid
    print("\nLayout:")
    for row in grid:
        print(' '.join(row))
    print()

def test_optimisation():
    #print("Creating layout...")  # Debug print
    # Create a simple layout
    layout = Layout(width=10, length=10)
    
    #print("Adding walls and aisles...")  # Debug print
    # Add walls around the edges
    layout.structure['wall'] = []
    for x in range(0, layout.width + 2):
        layout.structure['wall'].append((x, 0))  # Top edge
        layout.structure['wall'].append((x, layout.length + 1))  # Bottom edge
    for y in range(0, layout.length + 2):
        layout.structure['wall'].append((0, y))  # Left edge
        layout.structure['wall'].append((layout.width + 1, y))  # Right edge
    
    # Add some internal walls
    layout.structure['wall'].extend([(1,1), (1,2), (2,1)])
    
    #print("Adding entities...")  # Debug print
    # Add some entities
    layout.add_entities([
        {"type": "itemA", "placement": "auto", "size": (1,1)},
        {"type": "itemB", "placement": "auto", "size": (1,1)},
        {"type": "itemC", "placement": "auto", "size": (1,1)},
        {"type": "itemD", "placement": "auto", "size": (1,1)}
    ])
    
    #print("Adding operations...")  # Debug print
    # Add some operations with valid positions
    layout.operations = [
        Operation((3,3), (8,8), 5),  # From bottom-left to top-right
        Operation((8,3), (3,8), 3)   # From bottom-right to top-left
    ]
    
    # Print initial layout
    print("Initial Layout:")
    print_layout(layout)
    
    #print("Creating optimizer...")  # Debug print
    # Create and run the optimizer
    gasim = Gasim(
        layout=layout,
        function=get_fitness,
        population_size=10,
        mutation_rate=0.1,
        crossover_rate=0.8,
        elite_size=2
    )
    
    #print("Initializing population...")  # Debug print
    # Initialize and run for a few generations
    gasim.initialize_population()
    
    #print("Starting optimization...")
    for i in range(20):  # Run for 5 generations
        #print(f"\nGeneration {i+1}:")  # Debug print
        gasim.evolve()
        best_fitness = gasim.best_fitness_history[-1]
        print(f"Generation {i+1}: Best fitness = {best_fitness:.4f}")
        
        # Print best layout of this generation
        best_layout = gasim.best_layouts(1)[0]
        print(f"Best layout from generation {i+1}:")
        print_layout(best_layout)
    
    # Get and print best layouts
    best_layouts = gasim.best_layouts(3)
    print("\nFinal Best Layouts:")
    for i, layout in enumerate(best_layouts):
        print(f"\nLayout {i+1}:")
        print("Fitness:")
        print(get_fitness(layout))
        print_layout(layout)
        print("Entities:")
        for entity in layout.entities:
            print(f"  {entity['type']} at {entity['position']}")

    

if __name__ == "__main__":
    print("Starting test...")  # Debug print
    test_optimisation() 