import random
import mesa
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from models.agents import ShelfAgent, StationAgent, RobotAgent, BoxAgent
from models.portrayal import portrayal
import numpy as np

class OptimiserModel(Model):
    """Model for warehouse optimization simulation"""
    
    def __init__(self, warehouse_type="standard", warehouse_size=10, shapes="rectangular", 
                 model="efficiency", shelves=4, stations=2):
        super().__init__()
        
        # Initialize parameters
        self.warehouse_type = warehouse_type
        self.width = self.height = int(warehouse_size)
        self.shapes = shapes
        self.model_type = model
        self.num_shelves = int(shelves)
        self.num_stations = int(stations)

        self.population_size = 10

        # Initialize grid and scheduler
        self.grid = MultiGrid(self.width, self.height, True)
        self.schedule = RandomActivation(self)
        
        # Metrics
        self.efficiency = 0
        self.steps = 0
        
        # Data collector for charts
        self.datacollector = DataCollector(
            model_reporters={"Efficiency": "efficiency"},
            agent_reporters={}
        )

        # Initialise the genetic algorithm
        self.population = self.initialize_population(self.population_size, warehouse_size, shelves, stations)
        self.best_individual = None
        self.current_generation = 0

        # Start data collection
        self.running = True
        self.datacollector.collect(self)

    def initialize_population(self, pop_size, warehouse_size, num_shelves, num_stations):
        """
        Initialize a population of warehouse layouts.
        Each layout is represented as a 2D grid with encoded entities:
        0 = empty space, 1 = shelf, 2 = station.
        """
        population = []

        for _ in range(pop_size):
            layout = np.zeros(shape=(warehouse_size, warehouse_size))
            
            # Randomly place shelves
            for _ in range(num_shelves):
                x, y = random.randint(0, warehouse_size - 1), random.randint(0, warehouse_size - 1)
                layout[x, y] = 1  # Corrected item assignment syntax

            # Randomly place stations
            for _ in range(num_stations):
                x, y = random.randint(0, warehouse_size - 1), random.randint(0, warehouse_size - 1)
                while layout[x, y] != 0:  # Avoid collisions
                    x, y = random.randint(0, warehouse_size - 1), random.randint(0, warehouse_size - 1)
                layout[x, y] = 2

            population.append(layout)

        return population

    def fitness_function(self, layout):
        """
        Fitness calculation:
        - Reward clear passages by counting empty cells connected in rows/columns.
        - Reward grouping by clustering shelves and stations.
        """
        score = 0

        # Reward clear passages (empty paths in rows/columns)
        for row in layout:
            score += np.sum([len(segment) for segment in np.split(row, np.where(row != 0)[0]) if np.all(segment == 0)])

        for col in layout.T:  # Transpose for vertical check
            score += np.sum([len(segment) for segment in np.split(col, np.where(col != 0)[0]) if np.all(segment == 0)])

        # Reward clustering of similar entities
        shelf_positions = np.argwhere(layout == 1)
        station_positions = np.argwhere(layout == 2)
        
        def cluster_score(positions):
            """Reward proximity by calculating Manhattan distances."""
            score = 0
            for i, pos1 in enumerate(positions):
                for pos2 in positions[i+1:]:
                    score += 1 / (1 + np.sum(np.abs(pos1 - pos2)))
            return score

        score += cluster_score(shelf_positions)
        score += cluster_score(station_positions)

        return score


    def crossover(self, parent1, parent2):
        """
        Perform crossover by combining rows from both parents.
        """
        split_point = random.randint(1, parent1.shape[0] - 1)
        child = np.vstack((parent1[:split_point], parent2[split_point:]))
        return child

    def mutate(self, layout, mutation_rate=0.1):
        """
        Perform mutation by randomly swapping elements within the layout.
        """
        if random.random() < mutation_rate:
            x1, y1 = random.randint(0, layout.shape[0] - 1), random.randint(0, layout.shape[1] - 1)
            x2, y2 = random.randint(0, layout.shape[0] - 1), random.randint(0, layout.shape[1] - 1)
            layout[x1, y1], layout[x2, y2] = layout[x2, y2], layout[x1, y1]
        return layout

    def run_genetic_algorithm_step(self):
        # Evaluate fitness of the population
        fitness_scores = [(individual, self.fitness_function(individual)) for individual in self.population]
        fitness_scores.sort(key=lambda x: x[1])  # Sort by fitness (lower is better)

        # Select the top individuals for reproduction
        top_individuals = [individual for individual, _ in fitness_scores[:self.population_size // 2]]

        # Generate new population through crossover and mutation
        new_population = []
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(top_individuals, 2)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)

        self.population = new_population
        self.best_individual = min(self.population, key=self.fitness_function)
        print(f'best individual - {self.fitness_function(self.best_individual)} -')
        print(self.best_individual)

    def step(self):
        # Run one step of the genetic algorithm
        self.run_genetic_algorithm_step()
        self.current_generation += 1

        # Clear existing agents
        for agent in self.schedule.agents.copy():
            self.grid.remove_agent(agent)
            self.schedule.remove(agent)

        # Add agents from the best layout
        for x in range(self.width):
            for y in range(self.height):
                if self.best_individual[x, y] == 1:
                    agent = ShelfAgent(self.next_id(), self)
                elif self.best_individual[x, y] == 2:
                    agent = StationAgent(self.next_id(), self)
                else:
                    continue
                # Check if cell is occupied before placing
                if not self.grid.get_cell_list_contents((x, y)):  
                    self.grid.place_agent(agent, (x, y))
                    self.schedule.add(agent)

        self.schedule.step()
        self.steps += 1

    def advance():
        pass

grid = CanvasGrid(portrayal, 10, 10, 500, 500)

# Define the server to visualise the genetic algorithm
server = mesa.visualization.ModularServer(OptimiserModel, [grid], "Genetic Algorithm for Box Placement")

if __name__ == "__main__":
    server.port = 8521
    server.launch()