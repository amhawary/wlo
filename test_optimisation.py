from models import Layout, Operation
from wlo.optimiser.algorithm.ga import Gasim
from optimiser.function.standard_layout_fitness import get_fitness, calc_utility_access
import matplotlib.pyplot as plt
import numpy as np
import csv

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

def plot_fitness_metrics(gasim, save_path="fitness_metrics.png"):
    """Plot fitness metrics over generations."""
    metrics = gasim.get_fitness_metrics()
    generations = range(1, len(metrics) + 1)
    
    # Get all metric names from the first individual of the first generation
    metric_names = list(metrics[0][0].keys())
    
    # Create subplots for each metric
    fig, axes = plt.subplots(len(metric_names), 1, figsize=(10, 5*len(metric_names)))
    if len(metric_names) == 1:
        axes = [axes]
    
    for i, metric_name in enumerate(metric_names):
        ax = axes[i]
        # Get values for this metric across all generations
        values = []
        for gen in metrics:
            gen_values = [ind[metric_name] for ind in gen]
            values.append(np.mean(gen_values))
        
        ax.plot(generations, values, 'b-', label='Average')
        ax.set_title(f'{metric_name} over Generations')
        ax.set_xlabel('Generation')
        ax.set_ylabel(metric_name)
        ax.grid(True)
        ax.legend()
    
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def save_metrics_to_csv(gasim, filename="fitness_metrics.csv"):
    """Save fitness metrics to a CSV file."""
    metrics = gasim.get_fitness_metrics()
    
    # Get all metric names from the first individual of the first generation
    metric_names = list(metrics[0][0].keys())
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        header = ['Generation']
        for metric in metric_names:
            header.extend([f'{metric}_min', f'{metric}_avg', f'{metric}_max'])
        writer.writerow(header)
        
        # Write data for each generation
        for gen_idx, gen_metrics in enumerate(metrics, 1):
            row = [gen_idx]
            for metric_name in metric_names:
                values = [ind[metric_name] for ind in gen_metrics]
                row.extend([min(values), sum(values) / len(values), max(values)])
            writer.writerow(row)
    
    print(f"\nFitness metrics have been saved to '{filename}'")
    print("The CSV file contains min, average, and max values for each metric in each generation.")

def create_sophisticated_layout():
    """Create a more sophisticated layout with meaningful zones and clusters."""
    layout = Layout(width=20, length=20)  # Larger layout for more flexibility
    
    # Add walls around the edges
    layout.structure['wall'] = []
    for x in range(0, layout.width + 2):
        layout.structure['wall'].append((x, 0))  # Top edge
        layout.structure['wall'].append((x, layout.length + 1))  # Bottom edge
    for y in range(0, layout.length + 2):
        layout.structure['wall'].append((0, y))  # Left edge
        layout.structure['wall'].append((layout.width + 1, y))  # Right edge
    
    # Create utility zones with more spread out positions
    layout.utilities = {
        'electric': [
            (3, 3),    # Power station 1
            (17, 3),   # Power station 2
            (10, 17)   # Power station 3
        ],
        'water': [
            (3, 17),   # Water source 1
            (17, 17)   # Water source 2
        ],
        'gas': [
            (10, 3),   # Gas supply 1
            (3, 10),   # Gas supply 2
            (17, 10)   # Gas supply 3
        ]
    }
    
    # Add internal walls to create more distinct zones
    # Manufacturing zone 1 walls
    for x in range(2, 7):
        layout.structure['wall'].append((x, 7))
    for y in range(2, 7):
        layout.structure['wall'].append((7, y))
        
    # Manufacturing zone 2 walls
    for x in range(13, 18):
        layout.structure['wall'].append((x, 7))
    for y in range(2, 7):
        layout.structure['wall'].append((13, y))
        
    # Storage zone walls
    for x in range(2, 7):
        layout.structure['wall'].append((x, 13))
    for y in range(13, 18):
        layout.structure['wall'].append((7, y))
    
    # Add entities with more varied initial positions
    # Manufacturing cluster 1 (needs power and water)
    manufacturing1 = [
        {"id": 1, "type": "machine_A", "placement": "auto", "size": (1,1), "depends_on": ["electric", "water"], "position": (3, 3)},
        {"id": 2, "type": "machine_A", "placement": "auto", "size": (1,1), "depends_on": ["electric", "water"], "position": (3, 5)},
        {"id": 3, "type": "machine_A", "placement": "auto", "size": (1,1), "depends_on": ["electric", "water"], "position": (5, 3)}
    ]
    
    # Manufacturing cluster 2 (needs power and gas)
    manufacturing2 = [
        {"id": 4, "type": "machine_B", "placement": "auto", "size": (1,1), "depends_on": ["electric", "gas"], "position": (15, 3)},
        {"id": 5, "type": "machine_B", "placement": "auto", "size": (1,1), "depends_on": ["electric", "gas"], "position": (15, 5)},
        {"id": 6, "type": "machine_B", "placement": "auto", "size": (1,1), "depends_on": ["electric", "gas"], "position": (17, 3)}
    ]
    
    # Storage cluster (no utility dependencies)
    storage = [
        {"id": 7, "type": "storage_A", "placement": "auto", "size": (1,1), "depends_on": ["none"], "position": (3, 15)},
        {"id": 8, "type": "storage_A", "placement": "auto", "size": (1,1), "depends_on": ["none"], "position": (3, 17)},
        {"id": 9, "type": "storage_B", "placement": "auto", "size": (1,1), "depends_on": ["none"], "position": (5, 15)},
        {"id": 10, "type": "storage_B", "placement": "auto", "size": (1,1), "depends_on": ["none"], "position": (5, 17)}
    ]
    
    # Utility-dependent standalone entities
    standalone = [
        {"id": 11, "type": "utility_station", "placement": "auto", "size": (1,1), "depends_on": ["electric", "water", "gas"], "position": (10, 10)},
        {"id": 12, "type": "charging_point", "placement": "auto", "size": (1,1), "depends_on": ["electric"], "position": (15, 15)}
    ]
    
    # Add all entities
    layout.add_entities(manufacturing1 + manufacturing2 + storage + standalone)
    
    # Add operations between different zones with varied frequencies
    layout.operations = [
        # Manufacturing to storage operations
        Operation((3,3), (3,15), 5),   # High frequency
        Operation((5,3), (5,15), 4),
        Operation((15,3), (3,17), 3),
        # Inter-manufacturing operations
        Operation((3,3), (15,3), 2),
        Operation((5,3), (17,3), 2),
        # Storage to storage operations
        Operation((3,15), (5,17), 1)   # Low frequency
    ]
    
    return layout

def test_optimisation():
    # Create a sophisticated layout
    layout = create_sophisticated_layout()
    
    # Print initial layout
    print("Initial Layout:")
    print_layout(layout)
    
    # Define custom weights for fitness calculation
    # Higher weights for metrics we want to optimize more
    weights = {
        'travel_distance': 2.0,    # Double weight for travel distance
        'congestion_risk': 1.5,    # 1.5x weight for congestion
        'turns': 1.0,              # Standard weight for turns
        'clustering': 3.0,         # Triple weight for clustering
        'utility_access': 2.0      # Double weight for utility access
    }
    
    # Create and run the optimizer with tuned parameters
    gasim = Gasim(
        layout=layout,
        function=lambda l: get_fitness(l, weights=weights),  # Use custom weights
        population_size=50,      # Larger population for more diversity
        mutation_rate=0.3,       # Higher mutation rate
        crossover_rate=0.7,      # Slightly lower crossover rate
        elite_size=5            # Keep more elites
    )
    
    # Initialize and run for generations
    gasim.initialize_population()
    
    best_fitness = float('-inf')
    generations_without_improvement = 0
    max_generations = 50
    improvement_threshold = 0.001  # Minimum improvement to consider
    min_generations = 20  # Minimum number of generations to run
    
    for i in range(max_generations):
        gasim.evolve()
        current_best = gasim.best_fitness_history[-1]
        
        # Check for improvement
        if current_best > best_fitness + improvement_threshold:
            best_fitness = current_best
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1
        
        # Print progress every 5 generations
        if i % 5 == 0:
            print(f"\nGeneration {i+1}:")
            print(f"Best fitness = {best_fitness:.4f}")
            
            # Print metrics for the best individual
            current_metrics = gasim.get_current_generation_metrics()
            best_metrics = max(current_metrics, key=lambda x: x['total_fitness'])
            print("Best individual metrics:")
            for metric, value in best_metrics.items():
                print(f"  {metric}: {value:.4f}")
        
        # Stop if no improvement for 15 generations AND we've run at least min_generations
        if generations_without_improvement >= 15 and i >= min_generations:
            print("\nStopping early - no improvement for 15 generations")
            break
    
    # Save metrics to CSV
    save_metrics_to_csv(gasim)
    
    # Get and print best layouts
    best_layouts = gasim.best_layouts(3)
    print("\nFinal Best Layouts:")
    for i, layout in enumerate(best_layouts):
        print(f"\nLayout {i+1}:")
        fitness, metrics = get_fitness(layout, weights=weights)
        print("Fitness metrics:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
        print_layout(layout)
        print("Entities:")
        for entity in layout.entities:
            print(f"  {entity['type']} at {entity['position']}")
    
    # Print fitness metrics history
    print("\nFitness Metrics History:")
    for gen, metrics in enumerate(gasim.get_fitness_metrics()):
        print(f"\nGeneration {gen + 1}:")
        for i, ind_metrics in enumerate(metrics):
            print(f"  Individual {i + 1}:")
            for metric, value in ind_metrics.items():
                print(f"    {metric}: {value:.4f}")

def test_utility_access():
    # Create a layout
    layout = Layout(width=10, length=10)
    
    # Add some utilities
    layout.utilities = {
        'electric': [(2,2), (8,8)],
        'water': [(5,5)],
        'gas': [(1,1)]
    }
    
    # Add entities with utility dependencies
    layout.entities = [
        {
            'id': 1,
            'category': 'machinery',
            'type': 'machineA',
            'position': (3,3),
            'depends_on': ['electric', 'water']
        },
        {
            'id': 2,
            'category': 'machinery',
            'type': 'machineB',
            'position': (7,7),
            'depends_on': ['electric', 'gas']
        },
        {
            'id': 3,
            'category': 'storage',
            'type': 'shelf',
            'position': (4,4),
            'depends_on': ['none']
        }
    ]
    
    # Calculate utility access score
    score = calc_utility_access(layout)
    
    # Expected score calculation:
    # machineA: 1/(1+1) + 1/(2+1) = 0.5 + 0.333 = 0.833
    # machineB: 1/(1+1) + 1/(6+1) = 0.5 + 0.143 = 0.643
    # Average: (0.833 + 0.643) / 2 = 0.738
    expected_score = 0.738
    
    # Allow for small floating point differences
    assert abs(score - expected_score) < 0.01, f"Expected score {expected_score}, got {score}"
    print(f"Utility access test passed with score: {score:.3f}")

if __name__ == "__main__":
    print("Starting test...")  # Debug print
    test_optimisation()
    test_utility_access() 