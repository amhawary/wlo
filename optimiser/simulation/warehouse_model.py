import random
import mesa
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from models.agents import ShelfAgent, StationAgent, BoxAgent
from models.portrayal import portrayal
import numpy as np

class WarehouseModel(Model):
    def __init__(self, layout):
        super().__init__()
        
        # Initialize parameters
        self.warehouse_type = warehouse_type
        self.width = self.height = int(warehouse_size)
        self.shapes = shapes
        self.model_type = model
        self.num_shelves = int(shelves)
        self.num_stations = int(stations)
        self.pace = int(pace)
        self.num_boxes = int(num_boxes)
        self.num_agents = int(num_agents)
        self.population_size = population_size
        
        # Initialize grid and scheduler
        self.grid = MultiGrid(self.width, self.height, True)
        self.schedule = BaseScheduler(self)
        
        # Metrics
        self.efficiency = 0
        self.steps = 0
        
        # Data collector for charts
        self.datacollector = DataCollector(
            model_reporters={"Efficiency": "efficiency"},
            agent_reporters={}
        )
        
        # Initialize the GA population for layouts (for shelves and stations)
        self.population = self.initialize_population(self.population_size, self.width, self.num_shelves, self.num_stations)
        self.best_individual = None
        self.current_generation = 0

        # Create dynamic agents based on GA layout (shelves & stations)
        self.update_layout_agents()
        
        # Create robot agents and boxes (static or separate from layout GA)
        self._create_boxes()
        
        # Start data collection
        self.running = True
        print("Initial shelf and station agents (from GA layout):")
        self.print_layout_agents()
    
    def initialize_population(self, pop_size, warehouse_size, num_shelves, num_stations):
        """
        Initialize a population of warehouse layouts.
        Each layout is represented as a 2D grid (numpy array) with encoded entities:
        0 = empty space, 1 = shelf, 2 = station.
        """
        population = []
        for _ in range(pop_size):
            layout = np.zeros((warehouse_size, warehouse_size), dtype=int)
            # Place shelves randomly
            for _ in range(num_shelves):
                x, y = random.randint(0, warehouse_size - 1), random.randint(0, warehouse_size - 1)
                layout[x, y] = 1
            # Place stations randomly (avoid collisions)
            for _ in range(num_stations):
                x, y = random.randint(0, warehouse_size - 1), random.randint(0, warehouse_size - 1)
                while layout[x, y] != 0:
                    x, y = random.randint(0, warehouse_size - 1), random.randint(0, warehouse_size - 1)
                layout[x, y] = 2
            population.append(layout)
        return population

    def fitness_function(self, layout):
        """
        Calculate fitness for a given layout.
        Lower fitness is better.
        Rewards clear passages (empty rows/cols segments) and clustering of shelves/stations.
        """
        score = 0
        # Clear passages: reward longer contiguous empty segments in rows/columns
        for row in layout:
            segments = np.split(row, np.where(row != 0)[0])
            score += sum(len(segment) for segment in segments if np.all(segment == 0))
        for col in layout.T:
            segments = np.split(col, np.where(col != 0)[0])
            score += sum(len(segment) for segment in segments if np.all(segment == 0))
        
        # Clustering: reward proximity of similar entities (shelves and stations)
        shelf_positions = np.argwhere(layout == 1)
        station_positions = np.argwhere(layout == 2)
        
        def cluster_score(positions):
            cs = 0
            for i, pos1 in enumerate(positions):
                for pos2 in positions[i+1:]:
                    cs += 1 / (1 + np.sum(np.abs(pos1 - pos2)))
            return cs
        
        score += cluster_score(shelf_positions)
        score += cluster_score(station_positions)
        return score

    def crossover(self, parent1, parent2):
        """Perform crossover by combining rows from both parents."""
        split_point = random.randint(1, parent1.shape[0] - 1)
        child = np.vstack((parent1[:split_point, :], parent2[split_point:, :]))
        return child

    def mutate(self, layout, mutation_rate=0.1):
        """Perform mutation by randomly swapping elements within the layout."""
        if random.random() < mutation_rate:
            x1, y1 = random.randint(0, layout.shape[0] - 1), random.randint(0, layout.shape[1] - 1)
            x2, y2 = random.randint(0, layout.shape[0] - 1), random.randint(0, layout.shape[1] - 1)
            layout[x1, y1], layout[x2, y2] = layout[x2, y2], layout[x1, y1]
        return layout

    def run_genetic_algorithm_step(self):
        """Perform one generation of the GA and update the population and best individual."""
        # Evaluate fitness for each individual
        fitness_scores = [(individual, self.fitness_function(individual)) for individual in self.population]
        # Sort by fitness (lower is better)
        fitness_scores.sort(key=lambda x: x[1])
        # Select top half for reproduction
        top_individuals = [ind for ind, score in fitness_scores[:self.population_size // 2]]
        
        # Generate new population via crossover and mutation
        new_population = []
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(top_individuals, 2)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)
        
        self.population = new_population
        # Best individual is the one with lowest fitness
        self.best_individual = min(self.population, key=self.fitness_function)
        print(f"Generation {self.current_generation}: Best fitness = {self.fitness_function(self.best_individual)}")
    
    def update_layout_agents(self):
        """
        Update shelf and station agents based on the best GA layout.
        Remove old shelf/station agents and place new ones according to the layout.
        """
        # Remove existing shelf and station agents
        for agent in self.schedule.agents.copy():
            if isinstance(agent, ShelfAgent) or isinstance(agent, StationAgent):
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
        
        if self.best_individual is None:
            # Use the first individual if GA hasn't run yet
            layout = self.population[0]
        else:
            layout = self.best_individual
        
        # Create agents based on layout
        for x in range(self.width):
            for y in range(self.height):
                if layout[x, y] == 1:
                    agent = ShelfAgent(self.next_id(), self)
                    self.grid.place_agent(agent, (x, y))
                    self.schedule.add(agent)
                elif layout[x, y] == 2:
                    # Here you can decide on pickup vs dropoff stations (for example, alternate)
                    is_pickup = ((x + y) % 2 == 0)
                    agent = StationAgent(self.next_id(), self, is_pickup=is_pickup)
                    self.grid.place_agent(agent, (x, y))
                    self.schedule.add(agent)
    
    def _create_boxes(self):
        """Create box agents at one of the pickup station positions."""
        # Get pickup stations (if any)
        pickup_stations = [agent for agent in self.schedule.agents if isinstance(agent, StationAgent) and agent.is_pickup]
        if not pickup_stations:
            return
        for _ in range(self.num_boxes):
            station = self.random.choice(pickup_stations)
            pos = station.pos
            box = BoxAgent(self.next_id(), self)
            self.grid.place_agent(box, pos)
            self.schedule.add(box)
    
    def print_layout_agents(self):
        """Print shelf and station agents by position for debugging."""
        for x in range(self.width):
            for y in range(self.height):
                cell_contents = self.grid.get_cell_list_contents((x, y))
                if cell_contents:
                    print(f"Agents at ({x}, {y}): {[agent.__class__.__name__ for agent in cell_contents]}")
    
    def calculate_efficiency(self):
        """Calculate current efficiency metric."""
        delivered_boxes = sum(1 for agent in self.schedule.agents 
                              if isinstance(agent, BoxAgent) and getattr(agent, 'delivered', False))
        if self.num_boxes > 0:
            return (delivered_boxes / self.num_boxes) * 100
        return 0
    
    def step(self):
        """Advance the model by one step, run GA, update layout, then step all agents."""
        # Run one generation of the GA
        self.run_genetic_algorithm_step()
        self.current_generation += 1
        
        # Update the layout (shelf & station agents) based on the best individual
        self.update_layout_agents()
        
        # (Optional) print updated layout agents for debugging
        print("Updated shelf/station agents:")
        self.print_layout_agents()
        
        # Step the scheduler (which steps all agents)
        self.schedule.step()
        self.steps += 1
        # Update efficiency metric
        self.efficiency = self.calculate_efficiency()
        self.datacollector.collect(self)
